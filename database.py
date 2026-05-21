import sqlite3
import bcrypt

def connect():
    return sqlite3.connect("delivery_food.db")

def create_tables(connection):
    with connection:
        connection.execute("""
                CREATE TABLE IF NOT EXISTS users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT DEFAULT 'user'
                    )
                    """)
    
        connection.execute("""
                CREATE TABLE IF NOT EXISTS restaurants(
                        id INTEGER PRIMARY KEY NOT NULL,
                        restaurant_name TEXT NOT NULL,
                        item_name TEXT NOT NULL,
                        price REAL NOT NULL, 
                        location TEXT NOT NULL
                    )
                    """)
    
        connection.execute("""
                CREATE TABLE IF NOT EXISTS cart(
                        user_id INTEGER,
                        restaurant_id INTEGER,
                        quantity INTEGER, 
                        PRIMARY KEY(user_id, restaurant_id),
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(restaurant_id) REFERENCES restaurants(id)
                    )
                    """)
    
        connection.execute("""
                CREATE TABLE IF NOT EXISTS orders(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        user_id INTEGER,
                        restaurant_id INTEGER,
                        total REAL,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(restaurant_id) REFERENCES restaurants(id)
                    )
                    """)
    
#-----USER FUNCTIONS-----
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

def add_user(connection, name, email, password):
    hashed = hash_password(password)
    try:
        with connection:
            connection.execute("""
                        INSERT INTO users(name, email, password) VALUES(?, ?, ?);
                            """, (name, email, hashed))
            return "success"
    except sqlite3.IntegrityError:
        return "already_exists"
    
def login_user(connection, email, password):
    user = connection.execute("SELECT id, name, password, role FROM users WHERE email=?", (email,)
                            ).fetchone()
    
    if user and bcrypt.checkpw(password.encode(), user[2].encode()):
        return user
    return None

def make_admin(connection, email):
    with connection:
        connection.execute("UPDATE users SET role='admin' WHERE email=?", (email,))

def get_user_password(connection, id):
    with connection:
        return connection.execute("SELECT password FROM users WHERE id=?", (id,)
                                ).fetchone()
    
def change_username(connection, id, name):
    with connection:
        connection.execute("UPDATE users SET name=? WHERE id=?", (name, id))

def change_password(connection, id, password):
    hashed = hash_password(password)
    with connection:
        connection.execute("UPDATE users SET password=? WHERE id=?", (hashed, id))

def delete_account_by_id(connection, id):
    with connection:
        connection.execute("DELETE FROM users WHERE id=?", (id,))



def add_restaurant(connection, id, restaurant_name, item_name, price, location):
    with connection:
        connection.execute("""
                        INSERT INTO restaurants(id, restaurant_name, item_name, price, location)
                        VALUES(?, ?, ?, ?, ?); """, (id, restaurant_name, item_name, price, location)
                        )
        
def get_menu(connection):
    with connection:
        return connection.execute("SELECT * FROM restaurants").fetchall()
    
def get_item_by_restaurant(connection, id):
    with connection:
        connection.execute("""
                        SELECT name, price FROM restaurants WHERE id=?""", (id,)).fetchall()
    
