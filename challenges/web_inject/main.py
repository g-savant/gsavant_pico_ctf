import base64
import hashlib
import os
import secrets
import sqlite3

from Crypto.Cipher import AES
from flask import Flask, jsonify, request, send_from_directory

# paths and config pulled from env
base_dir = os.path.abspath(os.path.dirname(__file__))
static_dir = os.path.join(base_dir, "static")
db_path = os.environ.get("USER_DB_PATH")
flag_path = os.environ.get("FLAG_PATH")
admin_pass_path = os.environ.get("ADMIN_PASS_PATH")
admin_user = os.environ.get("ADMIN_USERNAME")
db_key = os.environ.get("DB_KEY", "dev_db_key")
static_nonce = os.environ.get("GCM_NONCE", "stat1cn0nc3")
nonce_file = os.environ.get("NONCE_PATH", "/challenge/gcm_nonce")

# session and crypto setup
sessions = {}
session_cookie = "session"
aes_key = hashlib.sha256(db_key.encode()).digest()
nonce_bytes = static_nonce.encode()
nonce_bytes = nonce_bytes[:12]
if len(nonce_bytes) < 12:
    nonce_bytes = nonce_bytes.ljust(12, b"0")
fixed_nonce = nonce_bytes

# load flag/admin secrets from disk if they exist
flag_value = "picoCTF_dev_flag"
admin_password = "123"
if flag_path and os.path.exists(flag_path):
    with open(flag_path) as fh:
        flag_value = fh.read().strip()
if admin_pass_path and os.path.exists(admin_pass_path):
    with open(admin_pass_path) as fh:
        admin_password = fh.read().strip()
if nonce_file and os.path.exists(nonce_file):
    with open(nonce_file) as fh:
        val = fh.read().strip()
        if val:
            static_nonce = val
            fixed_nonce = static_nonce.encode()[:12].ljust(12, b"0")


# quick crypto helpers for passwords
def encrypt_password(password):
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=fixed_nonce)
    ciphertext, tag = cipher.encrypt_and_digest(password.encode())
    return (
        base64.b64encode(ciphertext).decode(),
        base64.b64encode(tag).decode(),
    )


def decrypt_password(ciphertext_b64):
    try:
        ciphertext = base64.b64decode(ciphertext_b64 or "")
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=fixed_nonce)
        return cipher.decrypt(ciphertext).decode(errors="ignore")
    except Exception:
        return ""


# start over each run to keep things simple
def init_db():
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute("DROP TABLE IF EXISTS users")
        conn.execute(
            "CREATE TABLE users(username TEXT PRIMARY KEY, nonce TEXT, password TEXT, tag TEXT, is_admin INTEGER)"
        )
        nonce_b64 = base64.b64encode(fixed_nonce).decode()
        cipher, tag = encrypt_password(admin_password)
        conn.execute(
            "INSERT INTO users(username, nonce, password, tag, is_admin) VALUES (?, ?, ?, ?, 1)",
            (admin_user, nonce_b64, cipher, tag),
        )
    conn.close()


app = Flask(__name__)

# make sure the db exists when the app loads
init_db()


@app.route("/login", methods=["POST"])
def login():
    # grab data from either json or form
    data = request.get_json(silent=True) or request.form.to_dict()
    username = data.get("username", "")
    password = data.get("password", "")

    # still building SQL with string formatting on purpose
    conn = sqlite3.connect(db_path)
    conn.executescript(
        f"""
        DROP TABLE IF EXISTS tmp_login;
        CREATE TEMP TABLE tmp_login(username TEXT, nonce TEXT, password TEXT, tag TEXT, is_admin INTEGER);
        INSERT INTO tmp_login
        SELECT username, nonce, password, tag, is_admin FROM users
        WHERE username = '{username}';
        """
    )
    row = conn.execute(
        "SELECT username, nonce, password, tag, is_admin FROM tmp_login LIMIT 1"
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"detail": "Bad login"}), 401

    decrypted = decrypt_password(row[2])
    if decrypted != password:
        return jsonify({"detail": "Bad login"}), 401

    # hand back some details and set a session
    token = secrets.token_hex(16)
    sessions[token] = {"username": row[0], "is_admin": bool(row[4])}
    resp = jsonify(
        {"username": row[0], "nonce_b64": row[1], "cipher": row[2], "tag": row[3]}
    )
    resp.set_cookie(session_cookie, token)
    return resp


@app.route("/register", methods=["POST"])
def public_register():
    # anybody can make an account
    data = request.get_json(silent=True) or request.form.to_dict()
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"detail": "Need username and password"}), 400

    nonce_b64 = base64.b64encode(fixed_nonce).decode()
    cipher, tag = encrypt_password(password)
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO users(username, nonce, password, tag, is_admin) VALUES (?, ?, ?, ?, 0)",
            (username, nonce_b64, cipher, tag),
        )
        created = conn.total_changes > 0
    conn.close()
    status = 201 if created else 200
    return (
        jsonify(
            {
                "status": "created" if created else "exists",
                "username": username,
            }
        ),
        status,
    )


@app.route("/admin/register", methods=["POST"])
def register():
    # only admin can mint new users
    data = request.get_json() or request.form.to_dict()
    token = request.cookies.get(session_cookie) or request.headers.get("Authorization") or data.get("token")
    sess = sessions.get(token)
    if not sess or not sess.get("is_admin"):
        return jsonify({"detail": "Admin only"}), 403

    username = data.get("username", "")
    password = data.get("password", "")
    is_admin = str(data.get("is_admin")).lower() in ("true", "1")

    nonce_b64 = base64.b64encode(fixed_nonce).decode()
    cipher, tag = encrypt_password(password)
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO users(username, nonce, password, tag, is_admin) VALUES (?, ?, ?, ?, ?)",
            (username, nonce_b64, cipher, tag, int(is_admin)),
        )
        created = conn.total_changes > 0
    conn.close()

    return jsonify(
        {
            "status": "created" if created else "exists",
            "username": username,
            "is_admin": is_admin,
        }
    )


@app.route("/admin/flag", methods=["POST"])
def admin_flag():
    # flag is for admins
    data = request.get_json(silent=True) or request.form.to_dict()
    token = request.cookies.get(session_cookie) or request.headers.get("Authorization") or data.get("token")
    sess = sessions.get(token)
    if not sess or not sess.get("is_admin"):
        return jsonify({"detail": "Admin only"}), 403
    return jsonify({"flag": flag_value})


@app.route("/")
def index():
    return send_from_directory(static_dir, "index.html")
