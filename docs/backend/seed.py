"""Run once: python seed.py  -> creates tables, a librarian, a member and sample books."""
import sqlite3
import config
from db import init_db
from auth import hash_password

init_db()
db = sqlite3.connect(config.DATABASE)
users = [
    ("Head Librarian", "admin@library.com", "admin123", "librarian"),
    ("Test Member", "member@library.com", "member123", "member"),
]
for name, email, pw, role in users:
    db.execute("INSERT OR IGNORE INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
               (name, email, hash_password(pw), role))
books = [
    ("Clean Code", "Robert C. Martin", "Programming", "9780132350884", 3),
    ("Effective Java", "Joshua Bloch", "Programming", "9780134685991", 2),
    ("Fluent Python", "Luciano Ramalho", "Programming", "9781492056355", 2),
    ("Dune", "Frank Herbert", "Sci-Fi", "9780441172719", 4),
    ("1984", "George Orwell", "Dystopian", "9780451524935", 5),
    ("Sapiens", "Yuval Noah Harari", "History", "9780062316097", 1),
]
for b in books:
    db.execute("INSERT OR IGNORE INTO books (title, author, genre, isbn, stock) VALUES (?,?,?,?,?)", b)
db.commit()
print("Seeded. Librarian: admin@library.com / admin123 | Member: member@library.com / member123")
