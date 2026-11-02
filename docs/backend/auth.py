import datetime, functools
import bcrypt, jwt
from flask import request, jsonify, g
import config
from db import get_db


def hash_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def check_password(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed.encode())


def make_token(user):
    payload = {
        "sub": str(user["id"]),
        "role": user["role"],
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")


def login_required(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="Missing token"), 401
        try:
            data = jwt.decode(header[7:], config.SECRET_KEY, algorithms=["HS256"])
        except jwt.PyJWTError:
            return jsonify(error="Invalid or expired token"), 401
        user = get_db().execute("SELECT * FROM users WHERE id = ?", (data["sub"],)).fetchone()
        if not user:
            return jsonify(error="User not found"), 401
        g.user = user
        return fn(*args, **kwargs)
    return wrapper


def librarian_required(fn):
    """RBAC: only staff may pass."""
    @functools.wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if g.user["role"] != "librarian":
            return jsonify(error="Librarian access only"), 403
        return fn(*args, **kwargs)
    return wrapper
