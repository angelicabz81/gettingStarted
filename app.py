"""
Programmer: Angelica Benitez
Project: Pocket Quince
"""


# Import Libraries
import os
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
import sqlite3

# Import functions from help.py
from help import apology, login_required, formatTime

# Import to save uploaded image
from fileinput import filename
from werkzeug.utils import secure_filename

app = Flask(__name__)



# Sourced from: https://docs.python.org/3/library/os.path.html#os.path.join
# For upload route
# Creates path to the folder for uploaded images, in / format: project/static/uploads
    # Hardcoding /static/uploads, Flask may have difficulty finding correct directory
# app.root_path is the absolute file system path to folder where main Flask file is/ to Flask base directory

#Absolute Path is the full system path to the directory where Flask app file is (where project folder is on computer)
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#DELETE: this basically tells the app where to save the uploaded dress images, by creating a folder path to it
# Then it stores that path in app.config so we can use it later


# Permitted file types for dress image uploads
ALLOWED_EXTENSIONS = {"png","jpg", "jpeg"}

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False # Sessions end when browser closes
app.config["SESSION_TYPE"] = "filesystem" #Session data held in local files
Session(app) # Activate Flask-Session with settings ^

# Path to SQLite database file
DATABASE = "wardrobe.db"

# Database connection management
# g is Flask object used to temporarily store daya
def get_db():
    if "db" not in g: # Check if database connection already exists
        g.db = sqlite3.connect(DATABASE) # Open database and store connection for reuse
        g.db.row_factory = sqlite3.Row # Enable dictionary-like row access for reading
    return g.db # Return database connection


# Closes database and clears g at end of EVERY request, Flask runs automatically
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None) # Extracts database connection, if exists
    if db is not None: # If database found
        db.close()


# Runs after every request, but before response is sent to user
# Prevents browser from saving old copies, always showed updated page
@app.after_request
def after_request(response): 
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user by taking in username, email, phone, password and password confirmation"""

    # User submits form via POST
    if request.method == "POST":

        db = get_db() # Establish database connection to wardrobe.db

        # Validate username, show error if empty
        username = request.form.get("username")
        if not username:
            return apology("Must provide username", 400) 

        # Validate email, show error if empty
        email = request.form.get("email")
        if not email:
            return apology("Must provide email", 400)

        # Validate phone number, show error if empty
        phone = request.form.get("phone")
        if not phone:
            return apology("Must provide phone", 400)

        # Validate password, show error if empty
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure both password and confirmation are typed in, and are identical
        if not password or not confirmation or password != confirmation:
            return apology("Input valid password", 400)

        # Check for duplicate username in users table, inputting username parameter as tuple
        # Tuple is container that can hold multiple items
        existing = db.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if existing is not None:
            return apology("Username already exists", 400)

        # Insert new user into users table, input parameters as tuple
        try:
            db.execute("INSERT INTO users (username, email, phone, hash) VALUES (?,?,?,?)",
                (username, email, phone, generate_password_hash(password)),)
            db.commit() # Save changes to database


        except sqlite3.IntegrityError: # UNIQUE username violated
            return apology("Username already exists", 400)
        except Exception: # Other errors
            return apology("Registration failed", 500)

        # Go to pre-login homepage 
        flash("You are registered!")
        return redirect("/")
    else:
        # Open registration page
        return render_template("register.html")

# Log in
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in with username and password"""

    session.clear() # Forget any user_id
    db = get_db() # Establish database connection to wardrobe.db

    # User submits form via POST
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchall()

        # Ensure username exists once and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], password
        ):
            return apology("Invalid username and/or password", 400)

        # Remember which user has logged in, holds the current user
        session["user_id"] = rows[0]["id"]

        # Redirect user to logged in home page
        return redirect("/")

    # User reached route via GET
    else:
        # Open Login page
        return render_template("login.html")

# Log out
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to pre login home page
    return redirect("/")

# Home page
@app.route("/")
def landingPage():
    """Redirect to home page based on session state"""

    if "user_id" in session: # If user is logged in
        return redirect("/catalog") # Go to dress catalog
    else: # If user is not logged in
        return render_template("index.html") # Go to title page

# Upload dress
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Allow user to upload dress, and add dress info to dresses table"""

    # User submits dress upload form, submits via POST
    if request.method == "POST":

        db = get_db() # Establish database connection to wardrobe.db

        # Validate size
        size = request.form.get("size")
        if not size:
            return apology("Must input size")

        # Validate Color
        color = request.form.get("color")
        if not color:
            return apology("Must input color")

        # Validate image presence
        image = request.files.get("dressImage")
        if not image:
            return apology("Must upload dress image")

        # Insert new dress into dresses table with tuple for size, color, and current user as owner
        cur = db.execute("INSERT INTO dresses (size, color, owner) VALUES (?,?,?)",
            (size, color, session["user_id"]),)
        db.commit() # Save database changes

        # Get the id of the newly inserted dress, as id in dresses is auto-incremented
        dress_id = cur.lastrowid

        # Cleans file name, then splits into its root(name) and file extension type(what's after .)
        root, ext = os.path.splitext(secure_filename(image.filename))

        # Creates new file name in format: dress_id.fileExtension
        filename = f"{dress_id}{ext}"

        # Builds full path to uploads folder for image, and saves that image in the folder
        # Ex: static/uploads/dress_id.fileExtension
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(filepath) # Writes image to file path

        # String containing URL generated by Flask for image file in static folder, usable by browser
        image_url = url_for("static", filename=f"uploads/{filename}")

        # Insert image url into dresses table for the correct id 
        db.execute("UPDATE dresses SET image_url = ? WHERE id = ?",
            (image_url, dress_id),)
        db.commit() # Commit database changes

        flash("Dress successfully uploaded")
        return redirect("/") # goes to homepage, maybe change later?
        #return render_template("test.html", image_url=image_url)# test displaying the image

    else:
        # get all dresses owned by the current user, and renter information
        db = get_db()

        # all dresses owned by user
        dressesBuffer = db.execute("SELECT * FROM dresses WHERE owner = ?", (session["user_id"],)).fetchall()

        dresses = []
        # append renter info, if any, to each dresses dictionary
        for dress in dressesBuffer:

            dress = dict(dress)  # Convert Row object to dictionary not readonly to allow changes
            renter = db.execute("SELECT users.id as renter_id,users.username, users.email, users.phone FROM users JOIN holdings ON users.id = holdings.user_id WHERE holdings.dress_id = ? AND holdings.rent_end IS NULL", (dress["id"],)).fetchone()
            
            if renter:
                dress["renter_id"] = renter["renter_id"]
                dress["renter"] = renter["username"]
                dress["renter_email"] = renter["email"]
                dress["renter_phone"] = renter["phone"]
            else:
                dress["renter_id"] = None
                dress["renter"] = None
                dress["renter_email"] = None
                dress["renter_phone"] = None

            dresses.append(dress)

        return render_template("upload.html", dresses=dresses)
    

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

    return render_template("catalog.html", catalog=catalog, formatTime=formatTime)


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

        return redirect("/holdings")# Go back to homepage

@app.route("/returnDress", methods=["POST"])
@login_required
def returnDress():

    dressId = request.form.get("dressId")
    db = get_db()

    #get selected dress ID
    if not dressId:
        return apology("No dress selected")
    
    #Check that dress is in currently rented(in user's holdings)
    rented = db.execute("SELECT 1 FROM holdings WHERE user_id = ? AND dress_id = ? AND rent_end IS NULL", (session["user_id"], dressId)).fetchone()
    if not rented:
        return apology("Dress is not currently rented")
    
    # Set rent_end to current time
    db.execute("UPDATE holdings SET rent_end = CURRENT_TIMESTAMP WHERE user_id = ? AND dress_id = ? AND rent_end IS NULL",(session["user_id"], dressId))
    db.commit()

    flash("Thank you for returning the dress!")
    return redirect("/")# Go back to homepage





# Holdings page
@app.route("/holdings")
@login_required
def holdings():
    db = get_db()

    holdingBuffer = db.execute("SELECT * FROM dresses JOIN holdings as h on dresses.id = h.dress_id WHERE h.user_id = ? AND h.rent_end IS NULL ORDER BY h.rent_start DESC", (session["user_id"],)).fetchall()

    #Add owner info to each holding
    holdings = []
    for holding in holdingBuffer:
        holding = dict(holding)  # Convert Row object to dictionary not readonly to allow changes

        holding["owner_id"] = holding["owner"]

        owner = db.execute("SELECT username, email, phone FROM users WHERE id = ?", (holding["owner"],)).fetchone()
        holding["owner_name"] = owner["username"]
        holding["owner_email"] = owner["email"]
        holding["owner_phone"] = owner["phone"]
        holdings.append(holding)
    return render_template("holdings.html", holdings=holdings)


#MESSAGES????
@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    db = get_db()

    #send a message
    if request.method == "POST":
        receiver_id = request.form.get("receiver_id")
        content = request.form.get("body")
        dress_id = request.form.get("dress_id")

        if not receiver_id or not content:
            return apology("Missing message information")

        db.execute("INSERT INTO messages (sender_id, receiver_id, dress_id, body) VALUES (?,?,?,?)",
                     (session["user_id"], receiver_id, dress_id, content)) 
        db.commit()

        flash("Message sent!")
        return redirect("/messages")
    else:
        #view messages
        messages = db.execute("SELECT messages.*, users.username as sender_name, dresses.image_url, dresses.size, dresses.color FROM messages JOIN users ON messages.sender_id = users.id LEFT JOIN dresses ON dresses.id = messages.dress_id WHERE messages.receiver_id = ? ORDER BY messages.created_at DESC", (session["user_id"],)).fetchall()
        return render_template("messages.html", messages=messages,formatTime=formatTime)




# in app.py
#source .venv/bin/activate
# python3 -m pip
# python3 -m flask --app app --debug run
if __name__ == "__main__":
    app.run(debug=True)

#sqlite_web wardrobe.db

