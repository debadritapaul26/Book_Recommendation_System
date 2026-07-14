import psycopg2
import os

# Paste the URL you got from Neon or Supabase here!
# In a real production app, you would hide this in a .env file
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    """Helper function to connect to the cloud database."""
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. AI Recommendations History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id SERIAL PRIMARY KEY,
            user_prompt TEXT, book_title TEXT, author TEXT,
            reason TEXT, rating TEXT, isbn TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Users Authentication Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL, 
            password_hash TEXT NOT NULL
        )
    ''')
    
    # 3. Materials Library Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL, title TEXT NOT NULL,
            author TEXT NOT NULL, isbn TEXT NOT NULL, rating TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- Materials Functions ---
def get_all_materials(category=None):
    conn = get_connection()
    cursor = conn.cursor()
    if category and category != "All":
        # In Postgres, we use %s instead of ? for variables
        cursor.execute('SELECT category, title, author, isbn, rating FROM materials WHERE category = %s', (category,))
    else:
        cursor.execute('SELECT category, title, author, isbn, rating FROM materials')
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- User Management Functions ---
def create_user(email, password_hash):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password_hash) VALUES (%s, %s)', (email, password_hash))
        conn.commit()
        conn.close()
        return True
    except psycopg2.IntegrityError:
        # Email already exists
        return False 

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email, password_hash FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_password(email, new_password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = %s WHERE email = %s', (new_password_hash, email))
    conn.commit()
    conn.close()

# --- Book History Functions ---
def save_logs(user_prompt, recommendations):
    conn = get_connection()
    cursor = conn.cursor()
    for book in recommendations:
        isbn = book.get('isbn', '') 
        cursor.execute('''
            INSERT INTO recommendations (user_prompt, book_title, author, reason, rating, isbn)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_prompt, book.get('title'), book.get('author'), book.get('reason'), book.get('rating'), isbn))
    conn.commit()
    conn.close()

def fetch_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_prompt, book_title, author, reason, rating, isbn FROM recommendations ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows