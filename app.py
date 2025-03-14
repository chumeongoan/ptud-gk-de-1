from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import sqlite3
import os
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database configuration
DATABASE = "blog.db"

# Database initialization
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        is_blocked BOOLEAN DEFAULT 0
    )
    ''')
    
    # Create posts table with image_url field
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        date TEXT NOT NULL,
        task TEXT DEFAULT 'Đã đăng',
        image_url TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def update_schema():
    """Add missing image_url column to posts table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if image_url column exists
    columns = [column[1] for column in cursor.execute('PRAGMA table_info(posts)')]
    
    if 'image_url' not in columns:
        print("Adding image_url column to posts table")
        cursor.execute('ALTER TABLE posts ADD COLUMN image_url TEXT')
        conn.commit()
    
    conn.close()

# User functions
def load_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return [dict(user) for user in users]

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(email, password, role="user", is_blocked=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (email, password, role, is_blocked) VALUES (?, ?, ?, ?)',
        (email, password, role, is_blocked)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def update_user(user_id, email=None, password=None, role=None, is_blocked=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current user data
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        return False
    
    email = email if email is not None else user['email']
    password = password if password is not None else user['password']
    role = role if role is not None else user['role']
    is_blocked = is_blocked if is_blocked is not None else user['is_blocked']
    
    cursor.execute(
        'UPDATE users SET email=?, password=?, role=?, is_blocked=? WHERE id=?',
        (email, password, role, is_blocked, user_id)
    )
    conn.commit()
    conn.close()
    return True

# Post functions
def load_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return [dict(post) for post in posts]

def get_post_by_id(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    return dict(post) if post else None

def get_posts_by_author(author):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts WHERE author = ? ORDER BY id DESC', (author,)).fetchall()
    conn.close()
    return [dict(post) for post in posts]

def create_post(title, content, author, date, task="Đã đăng"):
    # Generate a random Picsum image URL
    image_url = f"https://picsum.photos/800/400?random={random.randint(1, 1000)}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO posts (title, content, author, date, task, image_url) VALUES (?, ?, ?, ?, ?, ?)',
        (title, content, author, date, task, image_url)
    )
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return post_id

def update_post(post_id, title=None, content=None, author=None, date=None, task=None, image_url=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current post data
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        conn.close()
        return False
    
    title = title if title is not None else post['title']
    content = content if content is not None else post['content']
    author = author if author is not None else post['author']
    date = date if date is not None else post['date']
    task = task if task is not None else post['task']
    image_url = image_url if image_url is not None else post['image_url']
    
    cursor.execute(
        'UPDATE posts SET title=?, content=?, author=?, date=?, task=?, image_url=? WHERE id=?',
        (title, content, author, date, task, image_url, post_id)
    )
    conn.commit()
    conn.close()
    return True

def add_images_to_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all posts without image URLs
    posts = cursor.execute('SELECT id FROM posts WHERE image_url IS NULL').fetchall()
    
    for post in posts:
        # Generate a random Picsum image URL
        image_url = f"https://picsum.photos/800/400?random={random.randint(1, 1000)}"
        
        # Update the post with the new image URL
        cursor.execute('UPDATE posts SET image_url = ? WHERE id = ?', (image_url, post['id']))
    
    conn.commit()
    conn.close()
    print(f"Added images to {len(posts)} posts")

# Routes
@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    if not user:
        flash("Người dùng không tồn tại. Vui lòng đăng nhập lại.", "error")
        session.pop('user_id', None)
        return redirect(url_for('login'))
    
    if user['is_blocked']:
        flash("Tài khoản của bạn đã bị khóa.", "error")
        session.pop('user_id', None)
        return redirect(url_for('login'))
    
    # Convert to dict for template compatibility
    user = dict(user)
    
    # Get all posts and user posts
    conn = get_db_connection()
    all_posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    user_posts = conn.execute('SELECT * FROM posts WHERE author = ? ORDER BY id DESC', 
                             (user['email'],)).fetchall()
    conn.close()
    
    # Convert to list of dicts for template compatibility
    all_posts = [dict(post) for post in all_posts]
    user_posts = [dict(post) for post in user_posts]
    
    # Pagination
    per_page = 10
    total_user_posts = len(user_posts)
    total_user_pages = (total_user_posts + per_page - 1) // per_page
    start_user = (page - 1) * per_page
    end_user = start_user + per_page
    paginated_user_posts = user_posts[start_user:end_user]
    
    total_all_posts = len(all_posts)
    total_all_pages = (total_all_posts + per_page - 1) // per_page
    start_all = (page - 1) * per_page
    end_all = start_all + per_page
    paginated_all_posts = all_posts[start_all:end_all]
    
    return render_template(
        'index.html',
        user=user,
        user_posts=paginated_user_posts,
        total_user_pages=total_user_pages,
        all_posts=paginated_all_posts,
        total_all_pages=total_all_pages,
        page=page
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Get user from database
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                           (email, password)).fetchone()
        conn.close()
        
        if user:
            if user['is_blocked']:
                flash("Tài khoản của bạn đã bị khóa.", "error")
                return redirect(url_for('login'))
            
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('index'))
        else:
            flash("Email hoặc mật khẩu không đúng.", "error")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if email exists using SQLite
        user = get_user_by_email(email)
        if user:
            flash("Email đã tồn tại.", "error")
            return redirect(url_for('register'))
        
        # Create user using SQLite
        user_id = create_user(email, password)
        
        flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    flash("Đăng xuất thành công.", "success")
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user directly from database
    user = get_user_by_id(session['user_id'])
    if not user or user['role'] != 'admin':
        flash("Bạn không có quyền truy cập trang này.", "error")
        return redirect(url_for('index'))
    
    users = load_users()
    return render_template('admin.html', users=users, user=user)

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        flash("Người dùng không tồn tại. Vui lòng đăng nhập lại.", "error")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        post_id = create_post(
            title=title,
            content=content,
            author=user['email'],
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        flash("Bài viết đã được tạo thành công!", "success")
        return redirect(url_for('index'))
    
    return render_template('new_post.html', user=user)

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Update schema
    update_schema()
    
    # Add images to existing posts (run once)
    add_images_to_posts()
    
    app.run(debug=True)
