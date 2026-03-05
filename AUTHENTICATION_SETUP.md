# Authentication Setup Guide

## Overview
This adds login authentication to protect your movie ratings app with the Oscar night theme.

## Features
- Beautiful Hollywood premiere login page
- Secure password hashing (bcrypt)
- Session management
- Simple admin panel for user management
- Logout functionality

## Installation Steps

### 1. Install Required Packages
```bash
# On LXC
cd /root/movie-ratings
docker compose exec web pip install flask-login bcrypt --break-system-packages
```

### 2. Create Users Table
```bash
# Initialize the users database
docker compose exec web python /app/init_users.py
```

This creates an admin user:
- Username: `admin`
- Password: `admin123` (CHANGE THIS IMMEDIATELY!)

### 3. Restart Application
```bash
docker compose restart web
```

## Usage

### Login
Visit `http://192.168.2.16:5000` and you'll see the login page.

### Admin Panel
After logging in as admin, visit `http://192.168.2.16:5000/admin/users` to:
- View all users
- Add new users
- Delete users
- Change passwords

### Logout
Click "Logout" link in the header

## Security Notes

1. **Change default admin password immediately!**
2. Passwords are hashed with bcrypt (secure)
3. Sessions expire when browser closes
4. No password recovery (admin must reset)

## File Changes

New files added:
- `app/init_users.py` - Initialize users table
- `app/templates/login.html` - Login page
- `app/templates/admin_users.html` - User management

Modified files:
- `app/app.py` - Added authentication routes
- `app/templates/base.html` - Added logout link
- `requirements.txt` - Added dependencies

