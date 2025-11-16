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

import os
import csv
import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote
from string import Template

UPLOAD_DIR = "uploads"
CONFIG_FILE = "uploads.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Chargement des métadonnées persistées
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        uploads = json.load(f)
else:
    uploads = []


def save_config():
    """Sauvegarde la liste des uploads dans le fichier JSON."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(uploads, f, indent=2, ensure_ascii=False)


def next_available_filename(filename: str) -> str:
    """Génère un nouveau nom si un fichier existe déjà (ex: test.csv -> test_1.csv)."""
    base, ext = os.path.splitext(filename)
    counter = 1
    new_name = filename
    while os.path.exists(os.path.join(UPLOAD_DIR, new_name)):
        new_name = f"{base}_{counter}{ext}"
        counter += 1
    return new_name


class CSVServer(BaseHTTPRequestHandler):

    def _send_html(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        if self.path == "/":
            self.list_files()
        elif self.path.startswith("/view/"):
            filename = unquote(self.path[len("/view/"):])
            self.view_file(filename)
        else:
            self._send_html("<h1>404 Not Found</h1>", 404)

    def do_POST(self):
        if not self.path.startswith("/upload/"):
            self._send_html("<h1>404 Not Found</h1>", 404)
            return

        original_name = unquote(self.path[len("/upload/"):])
        if not original_name.endswith(".csv"):
            self._send_html("<h1>400 Bad Request</h1><p>Filename must end with .csv</p>", 400)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(content_length)

        # Gérer versionnement
        final_name = next_available_filename(original_name)
        filepath = os.path.join(UPLOAD_DIR, final_name)
        with open(filepath, "wb") as f:
            f.write(data)

        # Enregistrer les métadonnées
        record = {
            "ip": self.client_address[0],
            "filename": final_name,
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        uploads.append(record)
        save_config()

        self._send_html(f"<h1>✅ Upload réussi</h1><p>Fichier sauvegardé : {final_name}</p>")

    def list_files(self):
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
        for u in sorted(uploads, key=lambda x: x["datetime"], reverse=True):
            html += f"<tr><td>{u['ip']}</td><td><a href='/view/{u['filename']}'>{u['filename']}</a></td><td>{u['datetime']}</td></tr>"
        html += "</table></body></html>"
        self._send_html(html)

    def view_file(self, filename):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            self._send_html("<h1>404 Not Found</h1>", 404)
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
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                html += "<tr>" + "".join(
                    f"<th>{cell}</th>" if i == 0 else f"<td>{cell}</td>"
                    for cell in row
                ) + "</tr>"
        html += "</table><p><a href='/'>← Back to list</a></p></body></html>"
        self._send_html(html)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), CSVServer)
    print("✅ Server running on http://localhost:8080")
    server.serve_forever()

