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
from base64 import b32decode, b64encode
from urllib.parse import parse_qs
from struct import pack, unpack
from sqlite3 import connect
from string import Template
from hashlib import sha256
from os import urandom
from time import time
from hmac import new

twofa_tokens = {}

def verify_user(username, password):
    if username is None or password is None:
        return None

    conn = connect('database.db')
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

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.do_GET_error_managed()
        except Exception as e:
            self.send_error(500, message="Internal Server Error", explain=f"{e.__class__.__name__}: {e}")
    
    def do_GET_error_managed(self):
        if self.path == '/':
            self.serve_page('welcome.html')
        elif self.path == '/login.html':
            if self.is_authenticated():
                self.send_response(302)
                self.send_header('Location', '/mailbox')
                self.end_headers()
                return
            self.serve_page('login.html')
        elif self.path == '/contact.html':
            self.serve_page('contact.html')
        elif self.path == '/careers.html':
            self.serve_page('careers.html')
        elif self.path == '/mailbox' and self.is_authenticated():
            self.send_response(403, message="Forbidden")
            self.serve_page('mailbox.html', False)
        else:
            self.send_error(404, "Page not found")

    def do_POST(self):
        try:
            self.do_POST_error_managed()
        except Exception as e:
            print(e.__class__.__name__, e)
            self.send_error(500, message="Internal Server Error", explain=f"{e.__class__.__name__}: {e}")
    
    def do_POST_error_managed(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_params = parse_qs(post_data.decode('utf-8'))
            
            unique_id = post_params.get('uniqueId', [None])[0]
            if unique_id:
                code = post_params.get('code', [None])[0]
                if verify_2fa(unique_id, code):
                    self.send_response(302)
                    self.send_header('Location', '/mailbox')
                    self.send_header('Set-Cookie', 'auth_token=valid; Path=/; HttpOnly')
                    self.end_headers()
                else:
                    self.send_response(401)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"<html><body><h2>Code 2FA invalide</h2></body></html>")
                return None

            username = post_params.get('username', [None])[0]
            password = post_params.get('password', [None])[0]
            token = verify_user(username, password)

            if username and password and token:
                id_2fa = b64encode(urandom(16)).decode()
                twofa_tokens[id_2fa] = token
                self.serve_page('login2fa.html', id_2fa=id_2fa)
            else:
                self.send_response(401)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body><h2>Identifiant ou mot de passe incorrect</h2></body></html>")
    
    def serve_page(self, page, code: int = 200, message: str = None, **kwargs):
        try:
            with open(page, 'r') as f:
                content = Template(f.read()).safe_substitute(kwargs).encode()
                self.send_response(code, message=message)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "Page not found")
    
    def is_authenticated(self):
        cookies = self.headers.get('Cookie')
        return 'auth_token=valid' in cookies if cookies else False

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, address='127.0.0.1', port=8080):
    server_address = (address, port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()

