from flask import Flask, g
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
    return "Hello, Flask i love boba!!"

# in app.py
# python3 -m flask --app app --debug run
if __name__ == "__main__":
    app.run(debug=True)