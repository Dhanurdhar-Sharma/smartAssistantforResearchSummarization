import sqlite3

conn = sqlite3.connect('database.db')

# Create users table
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        profile_photo TEXT
    )
''')

# Create documents table
conn.execute('''
    CREATE TABLE IF NOT EXISTS document (
        doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        doc_path TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
''')

conn.commit()
conn.close()
