import sqlite3, os
from flask import g
import config


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(config.DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(config.DATABASE)
    with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
        db.executescript(f.read())
    db.commit()
    db.close()
