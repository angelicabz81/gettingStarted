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

/register:


