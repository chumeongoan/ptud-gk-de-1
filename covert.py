import json
import os
import sqlite3

# Define database path
DATABASE = "blog.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def migrate_json_to_sqlite():
    # Check if JSON files exist
    if os.path.exists("users.json") and os.path.exists("posts.json"):
        try:
            # Migrate users
            with open("users.json", "r", encoding='utf-8') as f:
                users = json.load(f)
                
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users")  # Clear existing data
            
            for user in users:
                cursor.execute(
                    'INSERT INTO users (id, email, password, role, is_blocked) VALUES (?, ?, ?, ?, ?)',
                    (user['id'], user['email'], user['password'], user['role'], user['is_blocked'])
                )
            
            # Migrate posts
            with open("posts.json", "r", encoding='utf-8') as f:
                posts = json.load(f)
                
            cursor.execute("DELETE FROM posts")  # Clear existing data
            
            for post in posts:
                cursor.execute(
                    'INSERT INTO posts (id, title, content, author, date, task) VALUES (?, ?, ?, ?, ?, ?)',
                    (post['id'], post['title'], post['content'], post['author'], post['date'], post['task'])
                )
            
            conn.commit()
            conn.close()
            print("Migration completed successfully")
            return True
        except Exception as e:
            print(f"Migration error: {e}")
            return False
    else:
        print("JSON files not found")
    return False

# Run the migration
migrate_json_to_sqlite()