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
    This is the layer that users see, implemented through Jinja templates in the '/templates' directory. These are styled through the stylesheet '/static/style.css'. Most templates, such as for catalog and holdings, insert data such as dress listings from routes. 

2. **Backend**
    This is where core logic is, in 'app.py'. Here a database connection is established, templates are rendered, server-side validation occurs, route handling, and session handling happens for users.

3. **Wardrobe Database**
    A SQLite database called wardrobe.db stores 4 tables: users, dresses, holdings, and messages. These tables keep track of users, all dresses, establishing dress owners and renters.


DATABASE DESIGN:

My program uses a SQLite database with 4 tables. I chose to use SQLite because of the smaller scale of this project. sqlite3 is a built in module, which allowed for more easy use with Flask.

1. users

CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
username TEXT NOT NULL UNIQUE, 
email TEXT NOT NULL, 
phone TEXT NOT NULL, 
hash TEXT NOT NULL
);

This table stores account information, specifically a user id, username, email, phone, and hash for hashed password.

While a username could have been used as the sole identifier for users, and the foreign key for identifying users in other tables, I chose to keep track of users in SQL queries and foreign keys through their id. 

I reference users.id in many tables as a foreign key: including messages, holdings, and dresses. Using the id makes this relationship much simpler because the column becomes an integer field where all rows have a value similar in length, while username length could vary. The varying length of usernames would also make searching for a specific user a lot slower. Additionally, in future iterations, I hope to allow users to change their usernames. If I used usernames as the main identifier for a user, I would have to continuously update the foreign key fields it is referencenced in, rather than just the username row in users. 

I chose to hash passwords for security concerns, to ensure in the case of data leaks, account passwords remain secure. 

2. dresses

CREATE TABLE dresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    size TEXT NOT NULL,
    color TEXT NOT NULL,
    owner INTEGER NOT NULL,
    image_url TEXT,
    time_posted TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner) REFERENCES users(id)
);

This tables holds information about all dresses uploaded by users. Specifically: a unique dress id for each dress, owner symbolizing the dress owner, size of the dress, color of the dress, image_url to the location of the dress image in files, and the time_posted for when the user uploaded a dress.

I chose to give each dress a unique identifier that is automatically assigned, to be able to serve as a reference in foreign keys for holdings and messages. For example, if two dresses are the same size and color, a unique dress id would help differentiate between the two when searching for a specific dress. 

Size, color, and owner are all collected from the user and cannot be null, which I specified to ensure users have sufficient information about a dress before renting, and can contact the owner about further information after they have rented a dress.

I included time_posted so the user knows how long a dress has been available for, which could potentially tell users about the dress's popularity among other users.

The largest design choice I made here was creating the foreign key owner, which references ids from the users table. Dress owners must have already made an account in order to have uploaded a dress, so as users they also have a user id. By establishing a relationship between dresses and users, I make sure that each dress uploaded belongs to an existing user and prevent a dress from being inserted with an invalid owner id(like if they do not exist). Foreign keys keep the data consistent in this way. 

3. holdings

CREATE TABLE holdings (
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
user_id INTEGER NOT NULL,
dress_id INTEGER NOT NULL,
rent_start TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
rent_end TEXT,
FOREIGN KEY (user_id) REFERENCES users(id),
FOREIGN KEY (dress_id) REFERENCES dresses(id)
);

This table keeps track of rental activity. Specifically it contains an id for the rental, the user renting the dress as user_id, the dress rented as dress_id, the time the dress is rented as rent_start, and the time the dress is returned as rent_end.

The main priority for this table was finding a way to check if a dress was available or not. I chose to do so using rent_start and rent_end. When a dress is rented, it is placed into the holdings table with  the rent_start value being the current time. A dress is actively being rented when rent_end is NULL. This would mean the dress is not available. A dress is made available again when rent_end is sent to a time. Additionally, a dress is available if it is not in the holdings table at all, as this would mean it has never been rented before.

An alternative I considered was simply having a TEXT column called rented in the dresses table that had either the value yes or no to show if a dress was rented. I would update this value whenever a user clicked either a select dress or return dress button. However, this implementation would have limited the amount of information I could collect about rentals, as it would not let me track all rental activity for each dress, only the most recent rental. Every time a dress was rented or returned, the previous rental information would be overwritten. Tracking availability with rent_start and rent_end, will allow future implementations to show rental history for all dresses to users. 

I chose to have two foreign keys, to users.id and dresses.id. This was because each dress rented has its own unique dress id, and establishing a relationship between dresses and holdings would allow me to connect that to the users table and find the owner of each dress rented out. Connecting users and holdings allows me to obtain information about the users renting each dress. 

4. messages

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id   INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    dress_id    INTEGER,
    body        TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id)   REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id),
    FOREIGN KEY (dress_id)    REFERENCES dresses(id)
);

This table keeps track of messages sent to renters and dress owners. Specifically, it holds an id for each message, the user id of the sender as sender_id, the user id of the receiver as receiver_id, the dress id the message concerns as dress_id, the actual message as body, and when the message was sent as created_at.

I chose to keep track of when the message was sent for use in future implementation, where I will display the time a message was sent to a user.

I established three foreign keys, to users.id twice, and to dresses.id. There are two references to users.id because there are two users involved in messages: senders and recievers, both of whom must be registered users on the site. This ensures consistent records with valid users. I referenced dresses.id in order to show recipients the specific dress a message is concerning, so I could then use the dresses table to get the dress image.


BACKEND:

Database connection:
I am able to execute SQL queries by establishing a connection to wardrobe.db with get_db().

get_db() works by using g, which is a Flask object used to TEMPORARILY store data. 
This function opens the database and stores the connection within g using 'sqlite3.connect(DATABASE)' where 'DATABASE' is the path to the SQLite database file "wardrobe.db"

I put in this request to make a connection in every route, and at the end of each request, g is automatically cleared and the database is closed. This happens due to teardown_appcontext. 

I chose to establish connections in this way to ensure issues with potential memory leaks and having to excessively open a database for querying multiple times within one route.

User authentication:
This is comprised of the routes '/register', '/login' and '/logout'.

Registering:
register.html and the route '/register' work together to register a user.

Within the Jinja template register.html is a form that uses the 'POST' method. As input elements, it collects username, email, phone, and password of a user. All of these values are saved under their 'name' defined within each of the five elements. I used the 'POST' method because it is safe for sensitive data because data is not visible in the URL. 'POST' is best used for changing data. Once the form is submitted, I defined its route to be '/register', leading back to the app.py file. I defined two option: 'POST' method and 'GET' method. 'POST' is for submitting registration and 'GET' is for opening the page itself. 

Within the 'POST' method I completed server-side validation. I did so by obtaining the information the user inputted using 'request.form.get()' and the name I defined for each element earlier, then checking if each element was empty. If elements were empty, I called helper function apology, that opened a page with an error message telling a user they must input those fields. I did also have client-side validation by using the 'required' tag in each input element within register.html, and the server-side validation is an extra layer of security. 

I checked that passwords were valid by checking that both the password and password confirmation weren't empty, then comparing the two with 'password != confirmation' to prompt an 'apology()' error message if this was the case.

Checking if username already exists is actually done through a SQL query. The SQL query I execute searches for one row in the users table that has the username the current user wants to use. If no row is outputted, then the username is available.

Officially registering a user actually means inserting a row into the users table corresponding to the user, using a SQL query of 'INSERT INTO'. I insert the values for the username, email, phone number, and password. The password is not inserted in its original form, but first hashed using the helper function generate_password_hash(password). This hashes the password and adds a layer of security to user information.


Logging in:
login.html and the route '/login' work together to log in a user. 

login.html contains a form with a 'POST' method, whose action is the '/login' method. It has input elements who take in the username and password, both given a 'name' for their value for use in the route. Elements are set as 'required' to ensure forms cannot be submitted without either element. 'POST' is used to keep sensitive information such as the password secure.

Once the form submits, the 'POST' method in the route is executed. Server-side validation occurs as the two elements are obtained by 'request.form.get()' using their defined name, then validated for non-emptiness. 

A user is logged in by first executing a SQL query searching for a row in the users table where the username matches the inputted user by 'WHERE username = ?', I chose not to input the user-inputted username directly to prevent SQL injection that could bring harm to the database. Then, I check if there is exactly one row returned, and call the helper function check_password_hash() to compare the inputted password to hashed password contained within users, here found in 'rows[0]["hash"].

The most important aspect of this function is setting the 'session["user_id"]' to the user id of the user logging in. Choosing to save the current user's id here allows for easy repeated use of the user's id, used when uploading dresses, renting, and sending messages. 

Logging out:
When a user logs out, I clear the session 'session.clear', clearing the user id that is saved. 


Home page: 
I chose to  assign two home pages, one for before a user logs in and one for logged in users. I chose to do this because I wanted users who have not logged in to have a welcoming page that encourages them to register for the site.

Both of these are assigned using the same route, '/'. I check if a user is logged in by checking if 'user_id' has a value, or 'if "user_id" in session'. If this is the case, I direct users to the main dress catalog as their homepage, redirecting them to the 'catalog' route in order for all available dresses to be calculated and displayed. If not, I direct users to the index.html page that has icons and information about the site's purpose, using 'render_template()'.