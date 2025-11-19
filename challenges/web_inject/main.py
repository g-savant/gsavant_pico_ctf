from flask import Flask, request, jsonify, send_from_directory
import os
import secrets
import sqlite3

base_dir = os.path.abspath(os.path.dirname(__file__))
static_dir = os.path.join(base_dir, "static")
db_path = os.environ.get("USER_DB_PATH")
flag_path = os.environ.get("FLAG_PATH")
admin_pass_path = os.environ.get("ADMIN_PASS_PATH")
admin_user = os.environ.get("ADMIN_USERNAME")

flag_value = ""
admin_password = ""
sessions = {}


def load_file(path, fallback):
    if os.path.exists(path):
        with open(path, "r") as fh:
            return fh.read().strip()
    return fallback


def init_db():
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users(id INTEGER, username TEXT, password TEXT, is_admin INTEGER)"
        )
        conn.execute(
            "INSERT OR REPLACE INTO users(username, password, is_admin) VALUES (?, ?, 1)",
            (admin_user, admin_password),
        )
    conn.close()


app = Flask(__name__)

flag_value = load_file(flag_path, "picoCTF_dev_flag")
admin_password = load_file(admin_pass_path, "123")
init_db()


def get_data():
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        return data
    return request.form.to_dict()


def get_token(data):
    token = request.headers.get("Authorization")
    if not token:
        token = request.args.get("token")
    if not token:
        token = data.get("token")
    return token


def need_session(token):
    info = sessions.get(token)
    if not info:
        return None
    return info


@app.route("/login", methods=["POST"])
def login():
    data = get_data()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        f"SELECT username, password, is_admin FROM users WHERE username = '{username}' AND password = '{password}' LIMIT 1"
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"detail": "Bad login"}), 401

    token = secrets.token_hex(16)
    sessions[token] = {"username": row[0], "is_admin": bool(row[2])}
    return jsonify({"token": token, "username": row[0], "is_admin": bool(row[2])})


@app.route("/admin/register", methods=["POST"])
def register():
    data = get_data()
    session = need_session(get_token(data))
    if not session or not session.get("is_admin"):
        return jsonify({"detail": "Admin only"}), 403

    username = data.get("username")
    password = data.get("password")
    is_admin = str(data.get("is_admin")).lower() in ("true", "1")

    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO users(username, password, is_admin) VALUES (?, ?, ?)",
            (username, password, int(is_admin)),
        )
    conn.close()

    return jsonify({"status": "created", "username": username, "is_admin": is_admin})


@app.route("/admin/flag", methods=["POST"])
def admin_flag():
    data = get_data()
    session = need_session(get_token(data))
    if not session or not session.get("is_admin"):
        return jsonify({"detail": "Admin only"}), 403
    return jsonify({"flag": flag_value})


@app.route("/")
def index():
    return send_from_directory(static_dir, "index.html")
