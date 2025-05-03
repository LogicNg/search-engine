import sqlite3

from flask import g

from api.app import app


def get_cursor():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("documents.db")
    return db.cursor()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
