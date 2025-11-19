import os

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


import sqlite3

app = Flask(__name__)

# Path to SQLite database file
DATABASE = "wardrobe.db"

# Database connection management
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row # Enable dictionary-like row access
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/")
def home():
    db = get_db()
    cursor = db.execute('SELECT * FROM dummy').fetchall()
    one = cursor[0]["boba"]
    return f"How many boba drinks!! {one}"








# in app.py
#source .venv/bin/activate
# python3 -m pip
# python3 -m flask --app app --debug run
if __name__ == "__main__":
    app.run(debug=True)

#sqlite_web wardrobe.db

