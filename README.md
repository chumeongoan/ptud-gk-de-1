# ptud-gk-de-1
Mssv 22721621

Họ và Tên : Phan Nhật Trường


# Blog Management System

A web-based blog management system built with Flask and SQLite that allows users to create, view, and manage blog posts with user authentication and role-based access.

## Features

- **User Authentication**
  - Registration and login system
  - Role-based access (admin, user)
  - Account blocking capability
  
- **Blog Post Management**
  - Create new posts
  - View all posts or filter by author
  - Update existing posts
  - Post status tracking

- **Admin Panel**
  - User management
  - Post moderation
  - Account blocking functionality

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/chumeongoan/ptud-gk-de-1
   cd ptud-gk-de-1

2. **Create a virtual environment**
   ```bash
   python -m venv venv

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

3. **Initialize the database**
   ```bash
   python init_db.py

## Usagge
 **Start application**
   ```bash
   python app.py


** Access the application

Open your browser and go to http://127.0.0.1:5000/
Register a new account or login with existing credentials
Default admin account

Email: admin@example.com
Password: 123