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

from base64 import b32encode
from sqlite3 import connect
from hashlib import sha256
from os.path import join
from os import urandom

conn = connect(join('website', 'database.db'))
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    token2fa TEXT NOT NULL
)
''')

def hash_password(password):
    return sha256(password.encode('utf-8')).hexdigest()

users = [
    ("mathilde.rousseau@sylphora-dynamics.test", hash_password("V3RyStr0ngP4$$w0rdF0rSylphora"), b32encode(urandom(10)).decode()),
    ("bertille.demoulin@sylphora-dynamics.test", hash_password("marseille"), b32encode(urandom(10)).decode()),
    ("henri.brosquet@sylphora-dynamics.test", hash_password("$up3rR4nd0mP4$$w0rd"), b32encode(urandom(10)).decode()),
    ("george.fayet@sylphora-dynamics.test", hash_password("$08g3f@1956"), b32encode(urandom(10)).decode()),
    ("nora.blin@sylphora-dynamics.test", hash_password("V3RyW34kP4$$w0rdF0rSylphora"), b32encode(urandom(10)).decode()),
]

cursor.executemany('''
INSERT OR IGNORE INTO users (username, password_hash, token2fa)
VALUES (?, ?, ?)
''', users)

conn.commit()
conn.close()
print("Base de données initialisée avec succès.")

