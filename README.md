you need to have downloaded:

python3
flask
everything in requirements.txt



try to submit without a username, then without a password

Pocket Quince
CS50 Final Project
Programmer: Angelica Benitez

Pocket-Quince is a dress-sharing platform created primarily for the Latino community, to provide support in quinceañera planning, a key milestone for 15 year old girls. 

My platform allows users to rent dresses and upload dresses for other users to browse through in a dress catalog. My goal is to make quinceañeras more financially accessible and sustainable for all users. 


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
    Flask is the web framework for routes in app.py. 

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

During development, **sqlite-web** was used to check data in my SQL tables. This is not necessary to run my project, but may be useful for testing.

    Install by:
    ```bash
    pip install sqlite-web

    Generate link to visually view database:
    ```bash
    sqlite_web wardrobe.db
    From here, you can follow or copy the link generated in the terminal

NOTE: ```bash signifies pieces of code to run in the terminal


