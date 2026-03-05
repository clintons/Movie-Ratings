#!/usr/bin/env python3
"""
Initialize users table and create default admin user
"""
import psycopg2
import bcrypt
import os

# Database connection - read from environment variables (matching docker-compose.yml)
conn = psycopg2.connect(
    host=os.environ.get('POSTGRES_HOST', 'db'),
    database=os.environ.get('POSTGRES_DB', 'movieratings'),
    user=os.environ.get('POSTGRES_USER', 'postgres'),
    password=os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    port=os.environ.get('POSTGRES_PORT', '5432')
)

cur = conn.cursor()

# Create users table
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Check if admin user exists
cur.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
admin_exists = cur.fetchone()[0] > 0

if not admin_exists:
    # Create default admin user
    password = 'admin123'
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cur.execute(
        "INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)",
        ('admin', password_hash, True)
    )
    print("✓ Created admin user (username: admin, password: admin123)")
    print("⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
else:
    print("✓ Admin user already exists")

conn.commit()
cur.close()
conn.close()

print("✓ Users table initialized successfully")
