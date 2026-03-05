from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
import bcrypt

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-secret-key-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'movieratings'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'db'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

OMDB_API_KEY = os.getenv('OMDB_API_KEY', '')
POSTER_DIR = '/app/static/posters'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, is_admin=False):
        self.id = id
        self.username = username
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, username, is_admin FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['is_admin'])
    return None

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_unique_values(column_name):
    """Get unique non-null values from a column"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT DISTINCT {column_name} 
        FROM movies 
        WHERE {column_name} IS NOT NULL AND {column_name} != ''
        ORDER BY {column_name}
    """)
    values = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return values

def fetch_and_save_poster(title, year, movie_id):
    """Fetch movie poster from OMDB API and save locally"""
    poster_path = f"{POSTER_DIR}/{movie_id}.jpg"
    
    # Check if poster already exists
    if os.path.exists(poster_path):
        return f"/static/posters/{movie_id}.jpg"
    
    if not OMDB_API_KEY:
        return "/static/posters/placeholder.jpg"
    
    try:
        # Query OMDB API
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
        if year:
            url += f"&y={year}"
        
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('Poster') and data['Poster'] != 'N/A':
            # Download poster image
            poster_response = requests.get(data['Poster'], timeout=10)
            if poster_response.status_code == 200:
                # Open and resize image
                img = Image.open(BytesIO(poster_response.content))
                img.thumbnail((300, 450), Image.Resampling.LANCZOS)
                img.save(poster_path, 'JPEG', quality=85)
                return f"/static/posters/{movie_id}.jpg"
    except Exception as e:
        print(f"Error fetching poster for {title}: {e}")
    
    return "/static/posters/placeholder.jpg"

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, username, password_hash, is_admin FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
            user = User(user_data['id'], user_data['username'], user_data['is_admin'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Movie routes (protected)
@app.route('/')
@login_required
def index():
    """Main page with paginated movie list"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    # Get sort, search, and filter parameters
    sort_by = request.args.get('sort', 'date_dad_watched')
    order = request.args.get('order', 'DESC')
    search = request.args.get('search', '')
    filter_category = request.args.get('category', '')
    filter_genre = request.args.get('genre', '')
    
    # Valid sort columns matching your requirements
    valid_sorts = {
        'date_dad_watched': 'date_dad_watched',
        'date_k_watched': 'date_k_watched',
        'year': 'year',
        'genre': 'genre',
        'k_rating': 'k_rating',
        'dad_rating': 'dad_rating',
        'spencer_rating': 'spencer_rating',
        'dad_category': 'dad_category',
        'title': 'title'
    }
    
    sort_column = valid_sorts.get(sort_by, 'date_dad_watched')
    order_dir = 'ASC' if order == 'ASC' else 'DESC'
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Build query with search and filters
    where_clauses = []
    params = []
    
    if search:
        where_clauses.append("LOWER(title) LIKE LOWER(%s)")
        params.append(f"%{search}%")
    
    if filter_category:
        where_clauses.append("dad_category = %s")
        params.append(filter_category)
    
    if filter_genre:
        where_clauses.append("genre = %s")
        params.append(filter_genre)
    
    where_clause = ""
    if where_clauses:
        where_clause = "WHERE " + " AND ".join(where_clauses)
    
    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM movies {where_clause}"
    cur.execute(count_query, params)
    total = cur.fetchone()['total']
    
    # Get movies with sorting and pagination
    query = f"""
        SELECT * FROM movies 
        {where_clause}
        ORDER BY {sort_column} {order_dir} NULLS LAST, id DESC
        LIMIT %s OFFSET %s
    """
    cur.execute(query, params + [per_page, offset])
    movies = cur.fetchall()
    
    # Fetch posters for movies (in background, don't block page load)
    for movie in movies:
        if not movie.get('poster_path'):
            poster_url = fetch_and_save_poster(movie['title'], movie['year'], movie['id'])
            # Update database with poster path
            cur.execute("UPDATE movies SET poster_path = %s WHERE id = %s", 
                       (poster_url, movie['id']))
            movie['poster_path'] = poster_url
        else:
            # Ensure poster path is set
            if not movie['poster_path']:
                movie['poster_path'] = "/static/posters/placeholder.jpg"
    
    conn.commit()
    cur.close()
    conn.close()
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    
    # Get unique categories and genres for dropdowns
    categories = get_unique_values('dad_category')
    genres = get_unique_values('genre')
    
    return render_template('index.html',
                         movies=movies,
                         page=page,
                         total_pages=total_pages,
                         sort_by=sort_by,
                         order=order,
                         search=search,
                         total=total,
                         categories=categories,
                         genres=genres,
                         filter_category=filter_category,
                         filter_genre=filter_genre)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_movie():
    """Add new movie"""
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Parse dates
        date_dad = request.form.get('date_dad_watched')
        date_k = request.form.get('date_k_watched')
        date_dad_watched = datetime.strptime(date_dad, '%Y-%m-%d').date() if date_dad else None
        date_k_watched = datetime.strptime(date_k, '%Y-%m-%d').date() if date_k else None
        
        # Parse year
        year_str = request.form.get('year')
        year = int(year_str) if year_str else None
        
        cur.execute("""
            INSERT INTO movies (
                date_dad_watched, date_k_watched, title, year,
                streaming, lang_country, genre,
                k_rating, dad_rating, spencer_rating,
                dad_category, imdb_link
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            date_dad_watched,
            date_k_watched,
            request.form['title'],
            year,
            request.form.get('streaming') or None,
            request.form.get('lang_country') or None,
            request.form.get('genre') or None,
            request.form.get('k_rating') or None,
            request.form.get('dad_rating') or None,
            request.form.get('spencer_rating') or None,
            request.form.get('dad_category') or None,
            request.form.get('imdb_link') or None
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('index'))
    
    # GET request - get unique values for dropdowns
    categories = get_unique_values('dad_category')
    genres = get_unique_values('genre')
    
    return render_template('add_movie.html', categories=categories, genres=genres)

@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    """Edit existing movie"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        # Parse dates
        date_dad = request.form.get('date_dad_watched')
        date_k = request.form.get('date_k_watched')
        date_dad_watched = datetime.strptime(date_dad, '%Y-%m-%d').date() if date_dad else None
        date_k_watched = datetime.strptime(date_k, '%Y-%m-%d').date() if date_k else None
        
        # Parse year
        year_str = request.form.get('year')
        year = int(year_str) if year_str else None
        
        cur.execute("""
            UPDATE movies SET
                date_dad_watched = %s,
                date_k_watched = %s,
                title = %s,
                year = %s,
                streaming = %s,
                lang_country = %s,
                genre = %s,
                k_rating = %s,
                dad_rating = %s,
                spencer_rating = %s,
                dad_category = %s,
                imdb_link = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            date_dad_watched,
            date_k_watched,
            request.form['title'],
            year,
            request.form.get('streaming') or None,
            request.form.get('lang_country') or None,
            request.form.get('genre') or None,
            request.form.get('k_rating') or None,
            request.form.get('dad_rating') or None,
            request.form.get('spencer_rating') or None,
            request.form.get('dad_category') or None,
            request.form.get('imdb_link') or None,
            movie_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('index'))
    
    # GET request - show form
    cur.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cur.fetchone()
    cur.close()
    conn.close()
    
    if not movie:
        return "Movie not found", 404
    
    # Get unique values for dropdowns (same as add_movie)
    categories = get_unique_values('dad_category')
    genres = get_unique_values('genre')
    
    return render_template('edit_movie.html', movie=movie, categories=categories, genres=genres)

@app.route('/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    """Delete movie"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
@login_required
def admin_add_user():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin') == 'on'
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)",
            (username, password_hash, is_admin)
        )
        conn.commit()
        message = f"User '{username}' created successfully"
        message_type = 'success'
    except psycopg2.IntegrityError:
        conn.rollback()
        message = f"Username '{username}' already exists"
        message_type = 'error'
    finally:
        cur.close()
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('admin_users.html', users=users, message=message, message_type=message_type)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s AND username != 'admin'", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/change-password', methods=['POST'])
@login_required
def admin_change_password():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    username = request.form.get('username')
    new_password = request.form.get('new_password')
    
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = %s WHERE username = %s", (password_hash, username))
    rows_affected = cur.rowcount
    conn.commit()
    cur.close()
    
    if rows_affected > 0:
        message = f"Password changed for user '{username}'"
        message_type = 'success'
    else:
        message = f"User '{username}' not found"
        message_type = 'error'
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('admin_users.html', users=users, message=message, message_type=message_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
