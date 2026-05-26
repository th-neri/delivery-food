import sqlite3
import bcrypt

def connect():
    connection = sqlite3.connect("delivery_food.db")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

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
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        restaurant_name TEXT NOT NULL,
                        location TEXT NOT NULL
                    )
                    """)
        
        connection.execute("""
                CREATE TABLE IF NOT EXISTS dishes(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        restaurant_id INTEGER NOT NULL,
                        dish_name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        price REAL NOT NULL,
                        FOREIGN KEY(restaurant_id) REFERENCES restaurants(id)
                    )
                    """)
    
        connection.execute("""
                CREATE TABLE IF NOT EXISTS cart(
                        user_id INTEGER,
                        dish_id INTEGER,
                        quantity INTEGER, 
                        PRIMARY KEY(user_id, dish_id),
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(dish_id) REFERENCES dishes(id)
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
        
        connection.execute("""
                CREATE TABLE IF NOT EXISTS order_items(
                        order_id INTEGER,
                        dish_id INTEGER,
                        quantity INTEGER,
                        price REAL,
                        FOREIGN KEY(order_id) REFERENCES orders(id),
                        FOREIGN KEY(dish_id) REFERENCES dishes(id)
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


#-----RESTAURANT FUNCTIONS-----
def add_restaurant(connection, restaurant_name, location):
    with connection:
        connection.execute("""
                        INSERT INTO restaurants(restaurant_name, location)
                        VALUES(?, ?); """, (restaurant_name, location)
                        )
        
def delete_restaurant(connection, id):
    with connection:
        connection.execute("DELETE FROM restaurants WHERE id=?", (id,))
        
def add_dish(connection, restaurant_id, dish_name, type, price):
    with connection:
        connection.execute("""
                        INSERT INTO dishes(restaurant_id, dish_name, type, price)
                        VALUES(?, ?, ?, ?); """, (restaurant_id, dish_name, type, price)
                        )
        
def get_menu(connection):
    with connection:
        return connection.execute("SELECT id, restaurant_name FROM restaurants").fetchall()
    
def get_dish_by_restaurant(connection, restaurant_id):
    with connection:
        return connection.execute("""
                        SELECT id, dish_name, type, price FROM dishes WHERE restaurant_id=?""", (restaurant_id,)).fetchall()
    
def delete_dish(connection, id):
    with connection:
        return connection.execute("DELETE FROM dishes WHERE id=?", (id,))
    

#-----CART FUNCTIONS-----
