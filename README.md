**Pocket Quince**
**CS50 Final Project**
**Programmer: Angelica Benitez**


OVERVIEW:
Pocket-Quince is a dress-sharing platform created primarily for the Latino community, to provide support for Quinceañeras, a key milestone for 15 year old girls. 

My platform allows users to rent dresses and upload dresses for other users to browse through in a dress catalog. My goal is to make Quinceañeras more financially accessible and sustainable for all users. 

This documentation serves as a user's manual for my project. My project was created on Visual Studio Code.


PROGRAM REQUIREMENTS:
You must have these installed onto your device to be able to run my program.

**python3**
    Python is the language my Flask app runs on
    Here is a downloading guide: https://www.python.org/downloads/
**pip**
    Pip is Python's package manager, allowing you to install Python libraries
    Pip should be downloaded automatically with Python download

    Check if pip is installed, this should print a version number:
    ```bash 
    pip --version
**Flask**
    Flask is the web framework for routes in app.py

    Install by:
    ```bash
    pip install flask
**Flask-Session**
    Extension of Flask for storing user session data in local files

    Install by:
    ```bash
    pip install flask-session
**Werkzeug**
    Python library Flask uses to hash passwords in app.py

    Check if requirement is satisfied, or installs: 
    ```bash
    pip install werkzeug
**All dependencies in my 'requirements.txt'**

    Dependencies are all Python packages needed for project
        
    Download all:
    ```bash 
    pip install -r requirements.txt

SQLite is used for database management, but Python has a built in sqlite3 module that is imported directly in the Python file app.py

NOTE: ```bash signifies pieces of code to run in the terminal


PROGRAM STRUCTURE:
    ├── app.py          # My main flask app
    ├── help.py         # Helper functions
    ├── wardrobe.db     # SQLite database
    ├── requirements.txt 
    ├── static/
    |   ├── uploads/    # Uploaded dress images
    |   ├── style.css 
    |   └── *.png       # Other icons/images
    └── templates/
        ├── catalog.html
        ├── error.html
        ├── holdings.html
        ├── index.html
        ├── login.html
        ├── upload.html
        ├── messages.html
        ├── register.html
        └── upload.html

CONFIGURATION:
There is no additional configuration, just installing dependencies. I have already defined necessary paths in app.py including:
    - Path to database wardrobe.db
    - Path to upload folder for dress images
    - Configure session with Flask-Session


HOW TO RUN APPLICATION:

    ``bash
    python3 app.py ``

    OR

    ``bash
    python3 -m flask --app app run``

    Once the Flask app is running, you will see a link in the terminal, which should look this this:
        http://127.0.0.1:5000
    Follow this link to see the site up and running

USING POCKET QUINCE:

As a first time user, you should see a welcome page. Here you will have the option to register for an account or log in to an existing account.

Register: 
Click on the register link and create an account by inputting a username, email, phone number, password and confirmation of password.

    Testing:
    Try to register an account with any missing fields. For any missing fields, you will get a pop up that tells you it is a required field. This is client-side validation.

    After creating an account, go back to the register page and try to register with the same username. You will get routed to an error page that tells you username already exists.

    Type in passwords that do not match up, you will get routed to an error page that tells you to input a valid password.

Log in:
Click on the log in page and enter your registered username and password.

    Testing:
    Try to login with a missing field. You will get a pop up that tells you it is a required field.

Catalog: 
This is the first and main page opened upon logging in. Here you will find all available dresses, and a selection bar for users to filter for specific sizes and colors. You can also rent the dresses from users.

    Testing:
    Select a size in sizes and press the filter button. You should see that only dresses labeled with that size pop up.

    Select a color in colors and press the filter button. You should see that only dresses labeled with that color pop up.

    Select multiple sizes and colors and press the filter button. You should see that dresses matching both size and color filters pop up. 

    Rent a dress by pressing the 'select dress' button. This dress should be removed from catalog and should now be viewable in your holdings page.

Holdings:
This page shows all dresses a user is currently renting. It displays each dress owner's username, email, and phone number, as well as the option to send a message to the owner and return the dress. 

    Testing: 
    Return a dress by pressing the 'return dress' button. This dress should be removed from the holdings page and should now be visible again in the catalog. 

    Try to send a message by pressing the 'send' button. If your message field is empty you get a popup telling you it is a required field.

Upload dress:
This page shows all dresses a user owns and has uploaded for rent, along with information about its rented status. Users are able to send messages to the renters. The user can upload a dress by specifying the size, color, and including an image of the dress.

    Testing:

    Try to upload a dress with any missing fields, you will get a popup that no image is selected or that you must select an item. 

    When uploading a photo, your Finder is opened and you will see any files that are not .jpeg, .png or .jpg are not available to be selected. 

Inbox:
This page shows all messages that have been sent to you by the people renting your dress or the people who own the dresses you have rented. 


During development, **sqlite-web** was used to check data in my SQL tables. This is not necessary to run my project, but may be useful for testing.

    Install by:
    ```bash
    pip install sqlite-web

    Generate link to visually view database:
    ```bash
    sqlite_web wardrobe.db
    From here, you can follow or copy the link generated in the terminal

    Alternatively running
    ```bash
    sqlite3 wardrobe.db
    Will give you access to run SQLite prompts to view the tables in wardrobe.db

    .tables outputs the tables in wardrobe.db
