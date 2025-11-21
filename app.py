import os

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
import sqlite3

from help import apology, login_required, lookup, usd

# Import to save uploaded image
from fileinput import filename
from werkzeug.utils import secure_filename

app = Flask(__name__)

# For Upload Route
# Creates path to the folder where all uploaded folders will be held, in / format: project/static/uploads
# Hardcoding /static/uploads, Flask may have difficulty finding correct directory
# app.root_path is the absolute file system path to folder where main Flask file is/ to Flask base directory
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png","jpg", "jpeg"}


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

"""
test page
@app.route("/")
def home():
    db = get_db()
    cursor = db.execute('SELECT * FROM dummy').fetchall()
    one = cursor[0]["boba"]
    return f"How many boba drinks!! {one}"
"""


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        db = get_db()
        # Validate username
        username = request.form.get("username")
        if not username:
            return apology("Must provide username", 400)


        # Validate email
        email = request.form.get("email")
        if not email:
            return apology("Must provide email", 400)

        print("test update")
        # Validate phone number
        phone = request.form.get("phone")
        if not phone:
            return apology("Must provide phone", 400)

        # Validate password
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not password or not confirmation or password != confirmation:
            return apology("Input valid password", 400)

        # Check for duplicate username
        existing = db.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if existing is not None:
            return apology("username already exists", 400)

        # ChatGPT suggested change: use parameter tuple to prevent SQL injection
        # Insert new user into users table (use parameter tuple and commit)
        try:
            db.execute(
                "INSERT INTO users (username, email, phone, hash) VALUES (?,?,?,?)",
                (username, email, phone, generate_password_hash(password)),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return apology("username already exists", 400)
        except Exception:
            return apology("Registration failed", 500)

        # Go to homepage
        flash("You are registered!")
        return redirect("/")
    else:
        return render_template("register.html")

# Log in
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    db = get_db()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        ).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        # THIS IS THE CURRENT USER LOGGED IN
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Log out
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Go to home page
@app.route("/")
@login_required
def index():
    return render_template("index.html")


# Upload dress to table
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():

    if request.method == "POST":

        db = get_db()
        # Validate size
        size = request.form.get("size")
        if not size:
            return apology("Must input size")

        # Validate Color
        color = request.form.get("color")
        if not color:
            return apology("Must input color")

        # Validate image file
        image = request.files.get("dressImage")
        if not image:
            return apology("Must upload dress image")

        # Insert new dress into dresses table (use parameter tuple and commit)
        cur = db.execute(
            "INSERT INTO dresses (size, color, owner) VALUES (?,?,?)",
            (size, color, session["user_id"]),
        )
        db.commit()

        # Get the id of the newly inserted dress
        dress_id = cur.lastrowid

        # Set file name to unique dress id.fileExtension
        #Split original file name into its root(name) and file extension type
        root, ext = os.path.splitext(secure_filename(image.filename))
        filename = f"{dress_id}{ext}"

        # Builds full path to uploads folder for image, and saves that image in the folder
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(filepath)

        # URL generated by flask to the image file, accesible by browser
        image_url = url_for("static", filename=f"uploads/{filename}")

        # Insert image url into dresses table for the correct id and commit
        db.execute(
            "UPDATE dresses SET image_url = ? WHERE id = ?",
            (image_url, dress_id),
        )
        db.commit()

        #return redirect("/") # goes to homepage, maybe change later?
        print("erhtgbjrtig")
        return render_template("test.html", image_url=image_url)# test displaying the image

    else:
        return render_template("upload.html")
    

# Show all dresses
@app.route("/catalog", methods = ["GET"])
@login_required
def catalog():
        
    sizes = request.args.getlist("size")
    colors = request.args.getlist("color")

    db = get_db()

    # Only select dress that are not owned by the current user, not in holdings, or no longer being rented
    catalog = db.execute("SELECT * FROM dresses WHERE id NOT IN ( SELECT dress_id FROM holdings WHERE rent_end IS NULL) AND owner != ?"
    ,( session["user_id"],)).fetchall()
    print("Catalog before filtering:", catalog)

    filtered = []
    for dress in catalog:

        if sizes and dress["size"] not in sizes:
            continue
        if colors and dress["color"] not in colors:
            continue 
        filtered.append(dress)
    catalog = filtered
    print("Catalog after filtering:", catalog)

    return render_template("catalog.html", catalog=catalog)


#Test Select dress
@app.route("/selectDress", methods=["GET", "POST"])
@login_required
def selectDress():

    if request.method == "POST":
        dressId = request.form.get("dressId")
        db = get_db()

        # Get selected dress ID
        if not dressId:
            return apology("No dress selected")
        flash("You have selected this dress!")

        #Check that dress is available
        available = db.execute("SELECT 1 FROM dresses WHERE id = ? AND owner != ? AND id NOT IN ( SELECT dress_id FROM holdings WHERE rent_end IS NULL)"
        ,( dressId, session["user_id"],)).fetchone()

        if not available:
            return apology("Dress is not available")

        # Add dress to user's holdings
        db.execute("INSERT INTO holdings (user_id, dress_id) VALUES (?, ?)", (session["user_id"], dressId))
        db.commit()

        return redirect("/")# Go back to homepage


# Holdings page
@app.route("/holdings")
@login_required
def holdings():
    db = get_db()

    holdings = db.execute("SELECT * FROM dresses where id IN ( SELECT dress_id FROM holdings WHERE user_id = ? AND rent_end IS NULL)", (session["user_id"],)).fetchall()
    return render_template("holdings.html", holdings=holdings)


# in app.py
#source .venv/bin/activate
# python3 -m pip
# python3 -m flask --app app --debug run
if __name__ == "__main__":
    app.run(debug=True)

#sqlite_web wardrobe.db

