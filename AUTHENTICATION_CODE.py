# Authentication additions for app.py
# Add these imports at the top after existing imports

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt

# Add after app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add User class

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

# Add login route (BEFORE the index route)

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

# Add @login_required decorator to EXISTING routes
# Change this:
# @app.route('/')
# def index():

# To this:
# @app.route('/')
# @login_required
# def index():

# Do the same for ALL existing routes: add_movie, edit_movie, delete_movie

# Add admin routes at the end of the file

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
    cur = conn.cursor()
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
        conn.close()
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    
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
    conn.close()
    
    if rows_affected > 0:
        message = f"Password changed for user '{username}'"
        message_type = 'success'
    else:
        message = f"User '{username}' not found"
        message_type = 'error'
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('admin_users.html', users=users, message=message, message_type=message_type)
