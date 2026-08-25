from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db
import functools

auth_bp = Blueprint('auth', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = query_db('SELECT id, name, email, profile_photo FROM users WHERE id = ?', (user_id,), one=True)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        existing_user = query_db('SELECT id FROM users WHERE email = ?', (email,), one=True)
        if existing_user:
            flash('Email address is already registered.', 'danger')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        user_id = execute_db(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            (name, email, password_hash)
        )
        
        session.clear()
        session['user_id'] = user_id
        flash('Account created successfully!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)
        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))

@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            
            if not name or not email:
                flash('Name and email cannot be empty.', 'danger')
            else:
                execute_db('UPDATE users SET name = ?, email = ? WHERE id = ?', (name, email, g.user['id']))
                flash('Profile updated successfully.', 'success')
                
        elif action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            
            user = query_db('SELECT password_hash FROM users WHERE id = ?', (g.user['id'],), one=True)
            if not check_password_hash(user['password_hash'], current_pw):
                flash('Current password is incorrect.', 'danger')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'danger')
            else:
                execute_db('UPDATE users SET password_hash = ? WHERE id = ?', (generate_password_hash(new_pw), g.user['id']))
                flash('Password updated successfully.', 'success')

        elif action == 'delete_account':
            execute_db('DELETE FROM users WHERE id = ?', (g.user['id'],))
            session.clear()
            flash('Your account has been deleted.', 'info')
            return redirect(url_for('auth.index'))

    return render_template('settings.html')