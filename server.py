#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    CyberAttackSimulation for CyberTalk
#    Copyright (C) 2025  CyberAttackSimulation

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

from http.server import BaseHTTPRequestHandler, HTTPServer
from os.path import join, dirname, exists, splitext
from csv import DictWriter, DictReader, reader
from urllib.parse import parse_qs, unquote
from json import loads, dumps, load, dump
from base64 import b32decode, b64encode
from os import urandom, makedirs
from struct import pack, unpack
from datetime import datetime
from string import Template
from sqlite3 import connect
from hashlib import sha256
from uuid import uuid4
from time import time
from hmac import new
from sys import exit

BASE_PATH = dirname(__file__)
PATH_WEBSITE = join(BASE_PATH, "website")
PATH_MAIL = join(BASE_PATH, "mails")
PATH_ARSENAL = join(BASE_PATH, "arsenal", "server")
PATH_PIXELTRACKING = join(PATH_ARSENAL, "pixeltracking")
PATH_DATABREACH = join(PATH_ARSENAL, "databreach")
PATH_CSV = join(PATH_ARSENAL, "csv")

WEBSITE_DATABASE = join(PATH_WEBSITE, 'database.db')
PIXELTRACKING_DATABASE = join(PATH_PIXELTRACKING, "data.csv")
CSV_DATABASE = join(PATH_CSV, "uploads.json")

PIXELTRACKING_IMAGE = join(PATH_PIXELTRACKING, "1x1.png")
PIXELTRACKING_CREATE_PAGE = open(join(PATH_PIXELTRACKING, "create.html"), "rb").read()
PIXELTRACKING_STATISTICS_PAGE = open(join(PATH_PIXELTRACKING, "statistics.html"), "rb").read()

CSV_FILES_PATH = join(PATH_CSV, "uploads")
makedirs(CSV_FILES_PATH, exist_ok=True)
CSV_FILES = []

##################################
# WEBSITE
##################################

twofa_tokens = {}

def verify_user(username, password):
    if username is None or password is None:
        return None

    conn = connect(WEBSITE_DATABASE)
    cursor = conn.cursor()
    
    hash_hex = sha256(password.encode('utf-8')).hexdigest()

    cursor.execute(f'SELECT token2fa FROM users WHERE username = "{username}" AND password_hash = "{hash_hex}";')
    row = cursor.fetchone()

    return row[0] if row else None
    
def totp(secret):
    remainder = len(secret) % 8
    if remainder == 1 or remainder == 3 or remainder == 6:
         return
    secret = b32decode(secret.upper() + "=" * ((8 - len(secret)) % 8))
    time_counter = pack(">Q", int(time() / 30))
    hash_ = new(secret, time_counter, "sha1").digest()
    index = hash_[-1] & 0x0F
    value = unpack(">L", hash_[index : index + 4])[0] & 0x7FFFFFFF
    return str(value)[-6 :].zfill(6)
    
def verify_2fa(unique_id, token):
    return totp(twofa_tokens.get(unique_id)) == token

##################################
# Pixel tracking
##################################

def init_pixel_tracking_database():
    """
    Create CSV file if it doesn't exist.
    """

    if exists(PIXELTRACKING_DATABASE):
        return None

    with open(PIXELTRACKING_DATABASE, "w", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=["id", "data", "count", "created_at"])
        writer.writeheader()

def load_pixel_tracking_database():
    """
    Load all data from CSV into dict.
    """

    # if not exists(PIXELTRACKING_DATABASE):
    #     init_csv()

    data = {}
    with open(PIXELTRACKING_DATABASE, newline="", encoding="utf-8") as file:
        reader = DictReader(file)
        for row in reader:
            data[row["id"]] = row

    return data

def save_pixel_tracking_database(data):
    """
    Save all dict data back into CSV.
    """

    with open(PIXELTRACKING_DATABASE, "w", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=["id", "data", "count", "created_at"])
        writer.writeheader()
        for row in data.values():
            writer.writerow(row)
    
##################################
# CSV viewer
##################################

def save_csv_database():
    """
    Save the upload list in the database.
    """

    with open(CSV_DATABASE, "w", encoding="utf-8") as file:
        dump(CSV_FILES, file, indent=4, ensure_ascii=False)


def get_csv_filename(filename: str) -> str:
    """
    Generate new and unique name (example: test.csv -> test_1.csv).
    """

    base, extension = splitext(filename)
    counter = 1
    new_name = filename
    while exists(join(CSV_FILES_PATH, new_name)):
        new_name = f"{base}_{counter}{extension}"
        counter += 1
    return new_name

class CyberAttackSimulationServer(BaseHTTPRequestHandler):

    PAGES_404 = {}

    def _send_html(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
        
    def _set_json_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def _set_png_headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.end_headers()
        
    def serve_binary(self, filename):
        with open(filename, 'rb') as file:
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.end_headers()
            self.wfile.write(file.read())
        
    def serve_page(self, page, code: int = 200, message: str = None, **kwargs):
        try:
            with open(page, 'r', encoding="utf-8") as file:
                content = Template(file.read()).safe_substitute(kwargs).encode()
                self.send_response(code, message=message)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "Page not found")
    
    def do_GET(self):
        try:
            self.do_GET_error_managed()
        except Exception as e:
            self.send_error(500, message="Internal Server Error", explain=f"{e.__class__.__name__}: {e}")
    
    def do_GET_error_managed(self):
        if self.path == "/" or self.path == "/index.html":                                                       # slides, Host: talks.local
            self.serve_page("index.html")
        elif self.path == '/mailbox.html' or self.path == '/hacked.html':                                        # mails, Host: mailbox.fr, attackers.c2
            self.serve_page(join(PATH_MAIL, self.path[1:]))
        elif self.path == '/search.html':                                                                        # Data breach, Host: data.breach.onion
            self.serve_page(join(PATH_DATABREACH, 'search_data_leak.html'))
        elif self.path == '/procedure_urgence_securite.pdf.lnk':                                                 # Malware download, Host: a.c2
            self.serve_binary(join(PATH_ARSENAL, '..', 'procedure_urgence_securite.pdf.lnk'))
        elif self.path == '/procedure_urgence_securite.zip':                                                     # Malware download, Host: a.c2
            self.serve_binary(join(PATH_ARSENAL, '..', 'procedure_urgence_securite.zip'))
        elif self.path == '/py':                                                                                 # Malware download, Host: a.c2
            self.serve_binary(join(PATH_ARSENAL, '..', 'malware.py'))
        elif self.path == '/procedure_urgence_securite.pdf':                                                     # Malware download, Host: a.c2
            self.serve_binary(join(PATH_MAIL, 'procedure_urgence_securite.pdf'))
        elif self.path == '/welcome.html' or self.path == '/contact.html' or self.path == '/careers.html':       # company website, Host: sylphora-dynamics.test
            self.serve_page(join(PATH_WEBSITE, self.path[1:]))
        elif self.path == '/login.html':                                                                         # company website, Host: sylphora-dynamics.test
            self.login_page()
        elif self.path == '/mailbox' and self.is_authenticated():                                                # company website, Host: sylphora-dynamics.test
            self.serve_page(join(PATH_WEBSITE, 'mailbox.html'), 403, message="Forbidden")
        elif self.path == "/api/results":                                                                        # Pixel Tracking, Host: pixeltracking.attackers.c2
            self.api_pixel_tracking()
        elif self.path == "/stats":                                                                              # Pixel Tracking, Host: pixeltracking.attackers.c2
            self.render_page(PIXELTRACKING_STATISTICS_PAGE)
        elif self.path == "/create":                                                                             # Pixel Tracking, Host: pixeltracking.attackers.c2
            self.render_page(PIXELTRACKING_CREATE_PAGE)
        elif self.path.startswith("/img/"):                                                                      # Pixel Tracking, Host: pixeltracking.attackers.c2
            self.pixel_tracking()
        elif self.path.startswith("/csv/list/"):                                                                 # CSV viewer, Host: csv.attackers.c2
            self.list_csv_files()
        elif self.path.startswith("/csv/view/"):                                                                 # CSV viewer, Host: csv.attackers.c2
            self.csv_viewer(unquote(self.path[10:]))
        else:
            self.page_404()

    def do_POST(self):
        try:
            self.do_POST_error_managed()
        except Exception as e:
            print(e.__class__.__name__, e)
            self.send_error(500, message="Internal Server Error", explain=f"{e.__class__.__name__}: {e}")
    
    def do_POST_error_managed(self):
        if self.path == "/api/create_link":                                                                      # Pixel Tracking, Host: pixeltracking.attackers.c2
            self.create_pixel_tracking_link()
        elif self.path == '/login':                                                                              # company website, Host: sylphora-dynamics.test
            self.login()
        elif self.path.startswith("/csv/upload/") and self.path.endswith(".csv"):                                # CSV viewer, Host: csv.attackers.c2
           self.upload_csv(unquote(self.path[12:]))
        else:
            self.page_404()
            
    def page_404(self):
        host = self.headers.get("Host")
        page = self.PAGES_404.get(host)
        if page is None:
            return self.send_error(404, message=None, explain="Page not found")
        page(self)
        
    def json_page_404(self):
        self._set_json_headers(404)
        self.wfile.write(dumps({"error": "Not found"}).encode())
        
    def read_request_body(self):
        content_length = int(self.headers['Content-Length'])
        return self.rfile.read(content_length)
        
    def read_request_body_form(self):
        return parse_qs(self.read_request_body().decode('utf-8'))
        
    def read_request_body_json(self):
        return loads(self.read_request_body() or "{}")
        
    ##################################
    # WEBSITE
    ##################################
    
    def page_401(self, page):
        self.send_response(401)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(page)
    
    def login_page(self):
        if self.is_authenticated():
            self.send_response(302)
            self.send_header('Location', '/mailbox')
            self.end_headers()
            return
        self.serve_page(join(PATH_WEBSITE, 'login.html'))
        
    def login(self):
        post_params = self.read_request_body_form()
        unique_id = post_params.get('uniqueId', [None])[0]
        if unique_id:
            return self.handle_2fa(unique_id, post_params)
            
        username = post_params.get('username', [None])[0]
        password = post_params.get('password', [None])[0]
        token = verify_user(username, password)

        if username and password and token:
            id_2fa = b64encode(urandom(16)).decode()
            twofa_tokens[id_2fa] = token
            return self.serve_page(join(PATH_WEBSITE, 'login2fa.html'), id_2fa=id_2fa)
        
        self.page_401(b"<html><body><h2>Identifiant ou mot de passe incorrect</h2></body></html>")
            
    def handle_2fa(self, unique_id, post_params):
        code = post_params.get('code', [None])[0]

        if verify_2fa(unique_id, code):
            self.send_response(302)
            self.send_header('Location', '/mailbox')
            self.send_header('Set-Cookie', 'auth_token=valid; Path=/; HttpOnly')
            return self.end_headers()
        
        self.page_401(b"<html><body><h2>Code 2FA invalide</h2></body></html>")
        
    def is_authenticated(self):
        cookies = self.headers.get('Cookie')
        return 'auth_token=valid' in cookies if cookies else False
    
    ##################################
    # Pixel tracking
    ##################################
    
    def create_pixel_tracking_link(self):
        payload = self.read_request_body_json()
    
        data_value = payload.get("data", "")
        uid = str(uuid4())

        all_data = load_pixel_tracking_database()
        all_data[uid] = {
            "id": uid,
            "data": data_value,
            "count": "0",
            "created_at": datetime.utcnow().isoformat()
        }
        save_pixel_tracking_database(all_data)

        link = f"http://{self.headers['Host']}/img/{uid}"
        self._set_json_headers()
        self.wfile.write(dumps({"id": uid, "link": link}).encode("utf-8"))
        
    def api_pixel_tracking(self):
        all_data = load_pixel_tracking_database()
        self._set_json_headers()
        self.wfile.write(dumps(list(all_data.values()), indent=4).encode("utf-8"))
        
    def render_page(self, page):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page)
        
    def pixel_tracking(self):
        uid = self.path[5:]
        all_data = load_pixel_tracking_database()
        if uid not in all_data:
            self.send_error(404, "ID not found")
            return

        count = int(all_data[uid]["count"]) + 1
        all_data[uid]["count"] = str(count)
        save_pixel_tracking_database(all_data)

        with open(PIXELTRACKING_IMAGE, "rb") as image:
            self._set_png_headers()
            self.wfile.write(image.read())
    
    ##################################
    # CSV viewer
    ##################################
    
    def list_csv_files(self):
        html = """
        <html><head><title>Uploaded CSVs</title>
        <style>
        body { font-family: Arial; margin: 40px; background: #f6f8fa; }
        table { border-collapse: collapse; width: 100%; background: white; box-shadow: 0 0 10px #ccc; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #0078D7; color: white; }
        tr:hover { background: #f1f1f1; }
        a { color: #0078D7; text-decoration: none; }
        a:hover { text-decoration: underline; }
        </style></head><body>
        <h1>📂 Uploaded CSV Files</h1>
        <table>
        <tr><th>IP</th><th>Filename</th><th>Date/Time</th></tr>
        """
        for u in sorted(CSV_FILES, key=lambda x: x["datetime"], reverse=True):
            html += f"<tr><td>{u['ip']}</td><td><a href='/csv/view/{u['filename']}'>{u['filename']}</a></td><td>{u['datetime']}</td></tr>"
        html += "</table></body></html>"
        self._send_html(html)
        
    def csv_viewer(self, filename):
        filepath = join(CSV_FILES_PATH, filename)
        if not exists(filepath):
            self._send_html("<html><body><h1>404 Not Found</h1></body></html>", 404)
            return

        html = f"""
        <html><head><title>View CSV - {filename}</title>
        <style>
        body {{ font-family: Arial; margin: 40px; background: #f6f8fa; }}
        table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 0 10px #ccc; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background: #0078D7; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        </style></head><body>
        <h1>📊 {filename}</h1>
        <table>
        """
        with open(filepath, newline='', encoding='utf-8') as file:
            csvfile = reader(file)
            for i, row in enumerate(csvfile):
                html += "<tr>" + "".join(
                    f"<th>{cell}</th>" if i == 0 else f"<td>{cell}</td>"
                    for cell in row
                ) + "</tr>"
        html += "</table><p><a href='/csv/list/'>← Back to list</a></p></body></html>"
        self._send_html(html)
        
    def upload_csv(self, original_name):
        data = self.read_request_body()
        final_name = get_csv_filename(original_name)
        filepath = join(CSV_FILES_PATH, final_name)

        with open(filepath, "wb") as file:
            file.write(data)

        record = {
            "ip": self.client_address[0],
            "filename": final_name,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        CSV_FILES.append(record)
        save_csv_database()

        self._send_html(f"<h1>✅ Upload réussi</h1><p>Fichier sauvegardé : {final_name}</p>")

def run(server_class=HTTPServer, handler_class=CyberAttackSimulationServer, address='127.0.0.1', port=8080):
    server_address = (address, port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}...')
    httpd.serve_forever()
    
def main() -> int:
    init_pixel_tracking_database()
    
    if exists(CSV_DATABASE):
        with open(CSV_DATABASE, "r", encoding="utf-8") as file:
            CSV_FILES.extend(load(file))

    CyberAttackSimulationServer.PAGES_404["pixeltracking.attackers.c2"] = CyberAttackSimulationServer.json_page_404
    run()
    return 0

if __name__ == '__main__':
    exit(main())

