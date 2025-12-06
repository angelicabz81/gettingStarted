**Pocket Quince**
**CS50 Final Project**
**Programmer: Angelica Benitez**


OVERVIEW:
Pocket-Quince is a web application that allows users to rent and upload Quinceañera dresses for others to rent.

This design document describes the technical implementation of the project. 
The application is primarily built with Flask for routing and templating, SQLite for data storage, server-side sessions for tracking current users, and file upload paths for storing dress images. 


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


THREE SYSTEM COMPONENTS:
These three aspects connect to create the full-stack web application.

1. **Frontend**
    This is the layer that users see, implemented through Jinja templates in the '/templates' directory. These are styled through the stylesheet '/static/style.css'. Most templates, such as for catalog and holdings, insert data from routes such as dress listings.

2. **Backend**
    This is where core logic is, in 'app.py'. Here a database connection is established, templates are rendered, server-side validation occurs, and session handling happens for users.

3. **Wardrobe Database**
    A SQLite database called wardrobe.db stores 4 tables: users, dresses, holdings, and messages. These tables keep track of users, all dresses, establishing dress owners and renters.

