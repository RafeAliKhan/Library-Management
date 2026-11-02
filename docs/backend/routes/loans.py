from datetime import date, timedelta
from flask import Blueprint, request, jsonify, g
import config
from db import get_db
from auth import login_required, librarian_required

bp = Blueprint("loans", __name__, url_prefix="/api")


def calc_fine(due_date_str, end_date=None):
    due = date.fromisoformat(due_date_str)
    end = end_date or date.today()
    days_late = (end - due).days
    return round(max(days_late, 0) * config.FINE_PER_DAY, 2)


@bp.post("/loans")
@login_required
def borrow():
    data = request.get_json(silent=True) or {}
    book_id = data.get("book_id")
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        return jsonify(error="Book not found"), 404
    if book["stock"] < 1:
        return jsonify(error="No copies available"), 409
    dup = db.execute(
        "SELECT 1 FROM loans WHERE user_id=? AND book_id=? AND returned_at IS NULL",
        (g.user["id"], book_id),
    ).fetchone()
    if dup:
        return jsonify(error="You already have this book"), 409
    today = date.today()
    due = (today + timedelta(days=config.LOAN_DAYS)).isoformat()
    db.execute(
        "INSERT INTO loans (user_id, book_id, borrowed_at, due_date) VALUES (?, ?, ?, ?)",
        (g.user["id"], book_id, today.isoformat(), due),
    )
    db.execute("UPDATE books SET stock = stock - 1 WHERE id = ?", (book_id,))
    db.commit()
    return jsonify(message="Borrowed", due_date=due), 201


@bp.post("/loans/<int:loan_id>/return")
@login_required
def return_book(loan_id):
    db = get_db()
    loan = db.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
    if not loan or loan["returned_at"]:
        return jsonify(error="Active loan not found"), 404
    if loan["user_id"] != g.user["id"] and g.user["role"] != "librarian":
        return jsonify(error="Not your loan"), 403
    fine = calc_fine(loan["due_date"])
    db.execute("UPDATE loans SET returned_at=?, fine=? WHERE id=?",
               (date.today().isoformat(), fine, loan_id))
    db.execute("UPDATE books SET stock = stock + 1 WHERE id = ?", (loan["book_id"],))
    db.commit()
    return jsonify(message="Returned", fine=fine)


@bp.get("/me/loans")
@login_required
def my_loans():
    rows = get_db().execute(
        """SELECT loans.*, books.title, books.author FROM loans
           JOIN books ON books.id = loans.book_id
           WHERE user_id = ? ORDER BY returned_at IS NOT NULL, due_date""",
        (g.user["id"],),
    ).fetchall()
    out, total_fines = [], 0.0
    for r in rows:
        d = dict(r)
        if not r["returned_at"]:
            d["fine"] = calc_fine(r["due_date"])
            d["overdue"] = d["fine"] > 0
        total_fines += d["fine"]
        out.append(d)
    return jsonify(loans=out, fine_balance=round(total_fines, 2))


@bp.get("/admin/overdue")
@librarian_required
def overdue():
    today = date.today().isoformat()
    rows = get_db().execute(
        """SELECT loans.id, loans.due_date, users.name, users.email, books.title
           FROM loans JOIN users ON users.id = loans.user_id
           JOIN books ON books.id = loans.book_id
           WHERE loans.returned_at IS NULL AND loans.due_date < ?
           ORDER BY loans.due_date""",
        (today,),
    ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["fine"] = calc_fine(r["due_date"])
        out.append(d)
    return jsonify(out)
