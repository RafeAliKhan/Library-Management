import sqlite3
from flask import Blueprint, request, jsonify
from db import get_db
from auth import login_required, librarian_required
from validation import require_fields, parse_int

bp = Blueprint("books", __name__, url_prefix="/api/books")


@bp.get("")
@login_required
def list_books():
    q = f"%{request.args.get('q', '').strip()}%"
    genre = request.args.get("genre", "").strip()
    sql = "SELECT * FROM books WHERE (title LIKE ? OR author LIKE ?)"
    params = [q, q]
    if genre:
        sql += " AND genre = ?"
        params.append(genre)
    sql += " ORDER BY title"
    rows = get_db().execute(sql, params).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.get("/genres")
@login_required
def genres():
    rows = get_db().execute("SELECT DISTINCT genre FROM books ORDER BY genre").fetchall()
    return jsonify([r["genre"] for r in rows])


@bp.get("/<int:book_id>")
@login_required
def get_book(book_id):
    row = get_db().execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not row:
        return jsonify(error="Book not found"), 404
    return jsonify(dict(row))


@bp.post("")
@librarian_required
def create_book():
    data = request.get_json(silent=True)
    err = require_fields(data, ["title", "author", "genre"])
    if err:
        return jsonify(error=err), 400
    stock, err = parse_int(data.get("stock", 1), "stock")
    if err:
        return jsonify(error=err), 400
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO books (title, author, genre, isbn, stock) VALUES (?, ?, ?, ?, ?)",
            (data["title"].strip(), data["author"].strip(), data["genre"].strip(),
             (data.get("isbn") or None), stock),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify(error="ISBN already exists"), 409
    return jsonify(id=cur.lastrowid), 201


@bp.put("/<int:book_id>")
@librarian_required
def update_book(book_id):
    data = request.get_json(silent=True) or {}
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        return jsonify(error="Book not found"), 404
    stock = book["stock"]
    if "stock" in data:
        stock, err = parse_int(data["stock"], "stock")
        if err:
            return jsonify(error=err), 400
    db.execute(
        "UPDATE books SET title=?, author=?, genre=?, stock=? WHERE id=?",
        (data.get("title", book["title"]), data.get("author", book["author"]),
         data.get("genre", book["genre"]), stock, book_id),
    )
    db.commit()
    return jsonify(message="Updated")


@bp.delete("/<int:book_id>")
@librarian_required
def delete_book(book_id):
    db = get_db()
    db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    return jsonify(message="Deleted")
