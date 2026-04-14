# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from models.database import Database
import hashlib

auth_bp = Blueprint('auth', __name__)
db = Database()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        password = request.form.get('password')
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE employee_id = %s AND password = %s",
                (employee_id, hashed_password)
            )
            user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['employee_id'] = user['employee_id']
            session['name'] = user['name']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('employee.camera'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))