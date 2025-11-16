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

"""
curl -X POST http://localhost:8000/api/create_link -d '{"data":"Bonjour"}' -H "Content-Type: application/json; charset=utf-8"
"""

import http.server
import socketserver
import json
import urllib.parse
import uuid
import csv
import os
from io import BytesIO
from datetime import datetime
from os.path import join

BASE_PATH = join("arsenal", "server", "pixeltracking")
DATA_FILE = "data.csv"
PORT = 8000
IMAGE_PATH = join(BASE_PATH, "1x1.png")
CREATE_PAGE = open(join(BASE_PATH, "create.html"), "rb").read()
STAT_PAGE = open(join(BASE_PATH, "statistics.html"), "rb").read()

def init_csv():
    """
    Create CSV file if it doesn't exist.
    """

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "data", "count", "created_at"])
            writer.writeheader()

def load_data():
    """
    Load all data from CSV into dict.
    """

    if not os.path.exists(DATA_FILE):
        init_csv()
    data = {}
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row["id"]] = row
    return data

def save_data(data):
    """
    Save all dict data back into CSV.
    """

    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "data", "count", "created_at"])
        writer.writeheader()
        for row in data.values():
            writer.writerow(row)

class MyHandler(http.server.BaseHTTPRequestHandler):

    def _set_json_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def _set_png_headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.end_headers()

    def do_POST(self):
        """
        Handle POST /api/create_link
        """

        if self.path == "/api/create_link":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body or "{}")

            data_value = payload.get("data", "")
            uid = str(uuid.uuid4())

            all_data = load_data()
            all_data[uid] = {
                "id": uid,
                "data": data_value,
                "count": "0",
                "created_at": datetime.utcnow().isoformat()
            }
            save_data(all_data)

            link = f"http://{self.headers['Host']}/img/{uid}"
            self._set_json_headers()
            self.wfile.write(json.dumps({"id": uid, "link": link}).encode("utf-8"))
        else:
            self._set_json_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_GET(self):
        """
        Serve the PNG and increment counter.
        """

        if self.path == "/api/results":
            all_data = load_data()
            self._set_json_headers()
            self.wfile.write(json.dumps(list(all_data.values()), indent=2).encode("utf-8"))
        elif self.path.startswith("/stats"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(STAT_PAGE)
        elif self.path.startswith("/create"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(CREATE_PAGE)
        elif self.path.startswith("/img/"):
            uid = self.path.split("/img/")[-1]
            all_data = load_data()
            if uid not in all_data:
                self.send_error(404, "ID not found")
                return

            count = int(all_data[uid]["count"]) + 1
            all_data[uid]["count"] = str(count)
            save_data(all_data)

            with open(IMAGE_PATH, "rb") as img:
                self._set_png_headers()
                self.wfile.write(img.read())
        else:
            self._set_json_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())


if __name__ == "__main__":
    init_csv()
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"✅ Server running on http://localhost:{PORT}")
        httpd.serve_forever()
