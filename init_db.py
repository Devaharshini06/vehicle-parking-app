import sqlite3

from app import app, db

with app.app_context():
    db.create_all()
    print("✅ Tables created successfully!")



# Connect to the SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('parking_app.db')
c = conn.cursor()

# USERS table (for normal users, admin is handled separately)
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
''')

# PARKING LOTS table
c.execute('''
CREATE TABLE IF NOT EXISTS parking_lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prime_location_name TEXT NOT NULL,
    address TEXT,
    pin_code TEXT,
    price_per_hour REAL NOT NULL,
    number_of_spots INTEGER
)
''')

# PARKING SPOTS table
c.execute('''
CREATE TABLE IF NOT EXISTS parking_spots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    spot_number INTEGER NOT NULL,
    status TEXT DEFAULT 'A' CHECK(status IN ('A', 'O')),
    FOREIGN KEY (lot_id) REFERENCES parking_lots(id)
)
''')

# RESERVATIONS table
c.execute('''
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spot_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    parking_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    leaving_timestamp TIMESTAMP,
    parking_cost REAL,
    FOREIGN KEY (spot_id) REFERENCES parking_spots(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database initialized with tables: users, parking_lots, parking_spots, reservations ✅")
