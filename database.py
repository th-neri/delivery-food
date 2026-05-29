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
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT DEFAULT 'user'
                    )
                    """)
    
        connection.execute("""
                CREATE TABLE IF NOT EXISTS restaurants(
                        restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        restaurant_name TEXT NOT NULL,
                        location TEXT NOT NULL
                    )
                    """)
        
        connection.execute("""
                CREATE TABLE IF NOT EXISTS dishes(
                        dish_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        restaurant_id INTEGER NOT NULL,
                        dish_name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        price REAL NOT NULL,
                        FOREIGN KEY(restaurant_id) REFERENCES restaurants(restaurant_id)
                    )
                    """)
    
        connection.execute("""
                CREATE TABLE IF NOT EXISTS cart(
                        user_id INTEGER,
                        dish_id INTEGER,
                        quantity INTEGER NOT NULL, 
                        PRIMARY KEY(user_id, dish_id),
                        FOREIGN KEY(user_id) REFERENCES users(user_id),
                        FOREIGN KEY(dish_id) REFERENCES dishes(dish_id)
                    )
                    """)
    
        connection.execute("""
                CREATE TABLE IF NOT EXISTS orders(
                        order_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        user_id INTEGER NOT NULL,
                        restaurant_id INTEGER NOT NULL,
                        total REAL NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(user_id),
                        FOREIGN KEY(restaurant_id) REFERENCES restaurants(restaurant_id)
                    )
                    """)
        
        connection.execute("""
                CREATE TABLE IF NOT EXISTS order_items(
                        order_id INTEGER NOT NULL,
                        dish_id INTEGER NOT NULL,
                        dish_name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL,
                        PRIMARY KEY(order_id, dish_id),
                        FOREIGN KEY(order_id) REFERENCES orders(order_id),
                        FOREIGN KEY(dish_id) REFERENCES dishes(dish_id)
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
    user = connection.execute("SELECT user_id, name, password, role FROM users WHERE email=?", (email,)
                            ).fetchone()
    
    if user and bcrypt.checkpw(password.encode(), user[2].encode()):
        return user
    return None

def make_admin(connection, email):
    with connection:
        connection.execute("UPDATE users SET role='admin' WHERE email=?", (email,))

def get_user_password(connection, user_id):
    with connection:
        return connection.execute("SELECT password FROM users WHERE user_id=?", (user_id,)
                                ).fetchone()
    
def change_username(connection, user_id, name):
    with connection:
        connection.execute("UPDATE users SET name=? WHERE user_id=?", (name, user_id))

def change_password(connection, user_id, password):
    hashed = hash_password(password)
    with connection:
        connection.execute("UPDATE users SET password=? WHERE user_id=?", (hashed, user_id))

def delete_account_by_id(connection, user_id):
    with connection:
        connection.execute("DELETE FROM users WHERE user_id=?", (user_id,))


#-----RESTAURANT FUNCTIONS-----
def add_restaurant(connection, restaurant_name, location):
    with connection:
        connection.execute("""
                        INSERT INTO restaurants(restaurant_name, location)
                        VALUES(?, ?); """, (restaurant_name, location)
                        )
        
def delete_restaurant(connection, restaurant_id):
    with connection:
        connection.execute("DELETE FROM restaurants WHERE restaurant_id=?", (restaurant_id,))
        
def add_dish(connection, dish_name, restaurant_id, type, price):
    with connection:
        connection.execute("""
                        INSERT INTO dishes(dish_name, restaurant_id, type, price)
                        VALUES(?, ?, ?, ?); """, (dish_name, restaurant_id, type, price)
                        )
        
def delete_dish(connection, dish_id):
    with connection:
        return connection.execute("DELETE FROM dishes WHERE dish_id=?", (dish_id,))
        
def get_menu(connection):
    with connection:
        return connection.execute("SELECT restaurant_id, restaurant_name FROM restaurants").fetchall()
    
def get_dish_by_restaurant(connection, restaurant_id):
    with connection:
        return connection.execute("""
                        SELECT dish_id, dish_name, type, price FROM dishes WHERE restaurant_id=?""", (restaurant_id,)).fetchall()
    
def restaurant_exists(connection, restaurant_id):
    with connection:
        return connection.execute("SELECT restaurant_id FROM restaurants WHERE restaurant_id=?", (restaurant_id,)).fetchone()
    
def dish_exists(connection, dish_id):
    with connection:
        return connection.execute("SELECT dish_id FROM dishes WHERE dish_id=?", (dish_id,)).fetchone()
    

#-----CART FUNCTIONS-----
def add_to_the_cart(connection, user_id, dish_id, quantity):
    with connection:
        dish = connection.execute("SELECT dish_name, restaurant_id FROM dishes WHERE dish_id=?", (dish_id,)).fetchone()

        if not dish:
            return "dish_not_found"
        
        dish_name, restaurant_id = dish

        existing_restaurant = connection.execute("""
                                                SELECT
                                                dishes.restaurant_id
                                                FROM cart
                                                JOIN dishes ON cart.dish_id = dishes.dish_id
                                                WHERE cart.user_id=?
                                                LIMIT 1""", (user_id,)
                                                ).fetchone()
        
        if existing_restaurant:
            cart_restaurant_id = existing_restaurant[0]

            if cart_restaurant_id != restaurant_id:
                return "different_restaurant"

        existing = connection.execute("SELECT quantity FROM cart where user_id=? AND dish_id=?", (user_id, dish_id)).fetchone()

        if existing:
            connection.execute("""
                            UPDATE cart SET quantity = quantity + ? WHERE user_id=? AND dish_id=?""", (quantity, user_id, dish_id))
        else:
            connection.execute("""
                            INSERT INTO cart(user_id, dish_id, quantity) VALUES(?, ?, ?)""", (user_id, dish_id, quantity))
        
    return dish_name
        
def get_cart(connection, user_id):
    with connection:
        return connection.execute("""
                                  SELECT 
                                  dishes.dish_id,
                                  dishes.dish_name,
                                  dishes.price,
                                  dishes.restaurant_id,
                                  cart.quantity
                                  FROM cart 
                                  JOIN dishes ON cart.dish_id = dishes.dish_id
                                  WHERE cart.user_id=?""", (user_id,)
                                ).fetchall()
        
def delete_dish_from_cart(connection, user_id, dish_id):
    with connection:
        connection.execute("DELETE FROM cart WHERE user_id=? AND dish_id=?", (user_id, dish_id))

def checkout(connection, user_id):
    with connection:
        cart_items = connection.execute("""
                                        SELECT
                                        dishes.dish_id,
                                        dishes.dish_name,
                                        dishes.price,
                                        cart.quantity,
                                        dishes.restaurant_id
                                        FROM cart 
                                        JOIN dishes ON cart.dish_id = dishes.dish_id
                                        WHERE cart.user_id=?""", (user_id,)
                                        ).fetchall()
        if not cart_items:
            return "empty_cart"
        
        total = 0

        for item in cart_items:
            dish_id, name, price, quantity, restaurant_id = item

            total += price * quantity

        cursor = connection.execute("INSERT INTO orders(user_id, restaurant_id, total) VALUES(?, ?, ?)", (user_id, restaurant_id, total))

        order_id = cursor.lastrowid

        for item in cart_items:
            dish_id, name, price, quantity, restaurant_id = item

        connection.execute("INSERT INTO order_items(order_id, dish_id, dish_name, quantity, price) VALUES(?, ?, ?, ?, ?)", (order_id, dish_id, name, quantity, price))

        connection.execute("DELETE FROM cart WHERE user_id=?", (user_id,))

