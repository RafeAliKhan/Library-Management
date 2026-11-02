import re, sqlite3
from flask import Blueprint, request, jsonify, g
from db import get_db
from auth import hash_password, check_password, make_token, login_required
from validation import require_fields

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@bp.post("/register")
def register():
    data = request.get_json(silent=True)
    err = require_fields(data, ["name", "email", "password"])
    if err:
        return jsonify(error=err), 400
    if not EMAIL_RE.match(data["email"]):
        return jsonify(error="Invalid email"), 400
    if len(data["password"]) < 6:
        return jsonify(error="Password must be at least 6 characters"), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (data["name"].strip(), data["email"].lower().strip(), hash_password(data["password"])),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify(error="Email already registered"), 409
    return jsonify(message="Registered"), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True)
    err = require_fields(data, ["email", "password"])
    if err:
        return jsonify(error=err), 400
    user = get_db().execute(
        "SELECT * FROM users WHERE email = ?", (data["email"].lower().strip(),)
    ).fetchone()
    if not user or not check_password(data["password"], user["password_hash"]):
        return jsonify(error="Invalid email or password"), 401
    return jsonify(token=make_token(user), name=user["name"], role=user["role"])


@bp.get("/me")
@login_required
def me():
    u = g.user
    return jsonify(id=u["id"], name=u["name"], email=u["email"], role=u["role"])
