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


# Permitted file types for dress image uploads
ALLOWED_EXTENSIONS = {"png","jpg", "jpeg"}

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False # Sessions end when browser closes
app.config["SESSION_TYPE"] = "filesystem" #Session data held in local files
Session(app) # Activate Flask-Session with settings ^

# Path to SQLite database file
DATABASE = "wardrobe.db"

# Database connection management
# g is Flask object used to temporarily store data
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

        session.permanent = False

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
    """Allow user to upload dress, add dress info to dresses table, and show uploaded dresses"""

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

        flash("Dress uploaded!")
        return redirect("/") # goes to dress catalog
    
    else: # Show all dress owned by current user, and renter information if any

        db = get_db() # Establish database connection to wardrobe.db

        # Get all dress owned by user
        dressesBuffer = db.execute("SELECT * FROM dresses WHERE owner = ?", (session["user_id"],)).fetchall()

        dresses = [] # Empty list for dresses to be added to

        # Append renter info, if any, to each dresses dictionary
        for dress in dressesBuffer:
            dress = dict(dress)  # Convert row object to dictionary- so it's not readonly- to allow changes

            # Obtain renter of current dress if still rented out, with their id, username, email, and phone; Saved as dictionary
            renter = db.execute("SELECT users.id as renter_id, users.username, users.email, users.phone FROM users JOIN holdings ON users.id = holdings.user_id WHERE holdings.dress_id = ? AND holdings.rent_end IS NULL", (dress["id"],)).fetchone()

            if renter: # Check if dress is rented out

                # Key-Value pairs in dictionaries
                dress["renter_id"] = renter["renter_id"]
                dress["renter"] = renter["username"]
                dress["renter_email"] = renter["email"]
                dress["renter_phone"] = renter["phone"]

            else: # Dress is not rented out

                # Set values to None
                dress["renter_id"] = None
                dress["renter"] = None
                dress["renter_email"] = None
                dress["renter_phone"] = None

            dresses.append(dress) # Add new dress to total list, as dictionary

        # Open upload page, sending list of all dresses for display
        return render_template("upload.html", dresses=dresses)

# Show all dresses
@app.route("/catalog", methods = ["GET"])
@login_required
def catalog():
    """Obtain all dresses available for rent, allowing for filtering by color and size"""

    # Lists of user-selected filters    
    sizes = request.args.getlist("size") # User selected sizes
    colors = request.args.getlist("color") # User selected colors

    db = get_db() # Establish database connection to wardrobe.db

    # Select all dresses that are not owned by the current user, and not being rented out
        # Dress is rented out if dress is in holdings and rent_end is NULL, query excludes these dresses and where owner is current user
    catalog = db.execute("SELECT * FROM dresses WHERE id NOT IN ( SELECT dress_id FROM holdings WHERE rent_end IS NULL) AND owner != ?"
    ,( session["user_id"],)).fetchall()

    filtered = [] # Empty list that will hold dress fitting filters

    # Adds dresses that fit selected filters to filtered dress list
    for dress in catalog:

        # If user chose any desired sizes and current dress's size is not within this desired list
        if sizes and dress["size"] not in sizes:
            continue # Move on to next dress
        # If user chose any desired colors and current dress's colors is not within the desired list
        if colors and dress["color"] not in colors: 
            continue # Move on to next dress

        filtered.append(dress) # Add dress to list

    # Set full dress catalog to new list filtered list of dress
    catalog = filtered
     
    # Open catalog page with list of dresses for display, and formatTime helper function 
    return render_template("catalog.html", catalog=catalog, formatTime=formatTime)

# Rent dress
@app.route("/selectDress", methods=["GET", "POST"])
@login_required
def selectDress():
    """ Ensures selected dress is available, and moves rented dress to holdings table, keeping track of renter"""

    # If user clicks select dress button
    if request.method == "POST":

        db = get_db() # Establish database connection to wardrobe.db

        # Get selected dress ID, validate
        dressId = request.form.get("dressId")
        if not dressId:
            return apology("No dress selected")
        
        # Check that dress is available
        # Select dress that matches dress id, is not rented out, and does not belong to current user
        available = db.execute("SELECT 1 FROM dresses WHERE id = ? AND owner != ? AND id NOT IN ( SELECT dress_id FROM holdings WHERE rent_end IS NULL)"
        ,( dressId, session["user_id"],)).fetchone()

        if not available: # If query does not output a dress, dress is not available
            return apology("Dress is not available")

        flash("You have selected this dress!")

        # Add dress to holdings table, with dress id and user id
        db.execute("INSERT INTO holdings (user_id, dress_id) VALUES (?, ?)", (session["user_id"], dressId))

        db.commit() # Save database changes

        return redirect("/holdings")# Go to user's holdings page

# Return dress
@app.route("/returnDress", methods=["POST"])
@login_required
def returnDress():
    """Returns dress by setting rent_end column in holdings table to current time"""

    db = get_db() # Establish database connection to wardrobe.db
    
    # Get selected dress ID, validate
    dressId = request.form.get("dressId")
    if not dressId:
        return apology("No dress selected")
    
    # Check that dress is in currently rented out (in holdings, assigned to current user, rent_end is empty)
    rented = db.execute("SELECT 1 FROM holdings WHERE user_id = ? AND dress_id = ? AND rent_end IS NULL", (session["user_id"], dressId)).fetchone()

    if not rented: # If query does not output dress, dress is not currently rented by user
        return apology("Dress is not currently rented")
    
    # Return dress by setting rent_end to current time
    db.execute("UPDATE holdings SET rent_end = CURRENT_TIMESTAMP WHERE user_id = ? AND dress_id = ? AND rent_end IS NULL",(session["user_id"], dressId))
    db.commit() # Save database changes

    flash("Thank you for returning the dress!")
    return redirect("/")# Go back to catalog page

# Holdings
@app.route("/holdings")
@login_required
def holdings():
    """Gets dresses that user is currently renting out, from holdings table"""

    db = get_db() # Establish database connection to wardrobe.db

    # Selects all dresses user is renting out from holdings, where user id is current user's and rent_end is empty
    holdingBuffer = db.execute("SELECT * FROM dresses JOIN holdings as h on dresses.id = h.dress_id WHERE h.user_id = ? AND h.rent_end IS NULL ORDER BY h.rent_start DESC", (session["user_id"],)).fetchall()

    #Add dress owner's info to each holding
    holdings = [] # Empty list for all rented dresses

    for holding in holdingBuffer:
        holding = dict(holding)  # Convert Row object to dictionary not readonly to allow changes

        # Add new key of owner id, copying over value of "owner"
        holding["owner_id"] = holding["owner"]

        # Gets info on dress owner from users table: username, email, phone 
        owner = db.execute("SELECT username, email, phone FROM users WHERE id = ?", (holding["owner"],)).fetchone()

        # Adds each piece of info into holding dictionary
        holding["owner_name"] = owner["username"]
        holding["owner_email"] = owner["email"]
        holding["owner_phone"] = owner["phone"]

        holdings.append(holding) # Add updated dictionary to list

    # Open holdings page with list of dresses rented out
    return render_template("holdings.html", holdings=holdings)

# Messages
@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    """Allow users to send and view messages to owners of dresses they have rented"""
    
    db = get_db() # Set up database connection to wardrobe.db

    # Send a message
    if request.method == "POST":

        # Validate message content, dress id and receipient id
        receiver_id = request.form.get("receiver_id")
        content = request.form.get("body")
        dress_id = request.form.get("dress_id")

        if not receiver_id or not content or not dress_id:
            return apology("Missing message information")

        # Send message by inserting message content, recipient, and dress it correlates to into messages, with sender being current user
        db.execute("INSERT INTO messages (sender_id, receiver_id, dress_id, body) VALUES (?,?,?,?)",
                     (session["user_id"], receiver_id, dress_id, content)) 
        db.commit() # Save database changes

        flash("Message sent!")
        return redirect("/messages") # Allow for messages to be viewed
    
    # View messages
    else:
        # Select all messages where current user is recipient, along with information about the dress it concerns
        messages = db.execute("SELECT messages.*, users.username as sender_name, dresses.image_url, dresses.size, dresses.color FROM messages JOIN users ON messages.sender_id = users.id LEFT JOIN dresses ON dresses.id = messages.dress_id WHERE messages.receiver_id = ? ORDER BY messages.created_at DESC", (session["user_id"],)).fetchall()

        # Open message page, sending over all user messages
        return render_template("messages.html", messages=messages)

# Run Flask application
# python3 -m flask --app app --debug run
 
# Starts the Flask web server with debug mode
if __name__ == "__main__":
    app.run(debug=True)

#SQLITE viewer
#sqlite_web wardrobe.db