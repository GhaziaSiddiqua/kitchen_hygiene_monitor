# app.py - Complete working version with ALL features
from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_cors import CORS
import mysql.connector
import hashlib
from functools import wraps
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'your-secret-key-2024'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Database config - UPDATE YOUR PASSWORD HERE
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',  # Change this to your MySQL password
    'database': 'demo1'
}

def get_db():
    """Get database connection"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            return "Unauthorized", 403
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_camera'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        password = request.form.get('password')
        hashed = hashlib.md5(password.encode()).hexdigest()
        
        conn = get_db()
        if not conn:
            return render_template('login.html', error='Database connection error')
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE employee_id = %s AND password = %s", (employee_id, hashed))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['employee_id'] = user['employee_id']
            session['name'] = user['name']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('employee_camera'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    """Handle new user registration"""
    name = request.form.get('name')
    employee_id = request.form.get('employee_id')
    department = request.form.get('department')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Validation
    if not all([name, employee_id, department, password]):
        return redirect(url_for('login', error='All fields are required'))
    
    if password != confirm_password:
        return redirect(url_for('login', error='Passwords do not match'))
    
    if len(password) < 4:
        return redirect(url_for('login', error='Password must be at least 4 characters'))
    
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    conn = get_db()
    if not conn:
        return redirect(url_for('login', error='Database error'))
    
    cursor = conn.cursor()
    
    # Check if employee_id already exists
    cursor.execute("SELECT * FROM users WHERE employee_id = %s", (employee_id,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return redirect(url_for('login', error='Employee ID already exists'))
    
    try:
        # Insert into users table
        cursor.execute(
            "INSERT INTO users (employee_id, name, password, role) VALUES (%s, %s, %s, 'employee')",
            (employee_id, name, hashed_password)
        )
        
        # Insert into employees table
        cursor.execute(
            "INSERT INTO employees (employee_id, name, department) VALUES (%s, %s, %s)",
            (employee_id, name, department)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('login', success='Account created successfully! Please login.'))
    
    except Exception as e:
        print(f"Signup error: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return redirect(url_for('login', error='Error creating account. Please try again.'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/employee/camera')
@login_required
def employee_camera():
    return render_template('employee_camera.html', 
                         name=session.get('name'),
                         employee_id=session.get('employee_id'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/monitor')
@login_required
@admin_required
def admin_monitor():
    return render_template('admin_monitor.html')

@app.route('/api/log-violation', methods=['POST'])
@login_required
def log_violation():
    """Log a hygiene violation"""
    data = request.json
    employee_id = data.get('employee_id')
    violation_type = data.get('type')
    severity = data.get('severity', 'medium')
    
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database error'}), 500
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO violations (employee_id, type, severity, timestamp) VALUES (%s, %s, %s, NOW())",
        (employee_id, violation_type, severity)
    )
    conn.commit()
    violation_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'violation_id': violation_id})

@app.route('/api/get-violations')
@login_required
@admin_required
def get_violations():
    """Get all violations for admin dashboard"""
    conn = get_db()
    if not conn:
        return jsonify([])
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.*, e.name as employee_name, e.department
        FROM violations v
        JOIN employees e ON v.employee_id = e.employee_id
        ORDER BY v.timestamp DESC LIMIT 100
    """)
    violations = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert datetime to string for JSON serialization
    for v in violations:
        if v.get('timestamp'):
            v['timestamp'] = v['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify(violations)

@app.route('/api/get-stats')
@login_required
@admin_required
def get_stats():
    """Get statistics for admin dashboard"""
    conn = get_db()
    if not conn:
        return jsonify({'total': 0, 'today': 0, 'by_type': [], 'top_employees': []})
    
    cursor = conn.cursor(dictionary=True)
    
    # Total violations
    cursor.execute("SELECT COUNT(*) as total FROM violations")
    total = cursor.fetchone()['total']
    
    # Today's violations
    cursor.execute("SELECT COUNT(*) as today FROM violations WHERE DATE(timestamp) = CURDATE()")
    today = cursor.fetchone()['today']
    
    # Violations by type
    cursor.execute("""
        SELECT type, COUNT(*) as count 
        FROM violations 
        GROUP BY type
    """)
    by_type = cursor.fetchall()
    
    # Top employees with most violations
    cursor.execute("""
        SELECT e.name, COUNT(*) as count
        FROM violations v
        JOIN employees e ON v.employee_id = e.employee_id
        GROUP BY v.employee_id
        ORDER BY count DESC LIMIT 5
    """)
    top_employees = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'total': total,
        'today': today,
        'by_type': by_type,
        'top_employees': top_employees
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('login.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('login.html', error='Internal server error'), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🍽️ Kitchen Hygiene Monitor Starting...")
    print("="*50)
    print(f"🌐 Server running at: http://localhost:5000")
    print(f"👤 Admin Login: EMP006 / admin123")
    print(f"👤 Employee Login: EMP001 / 1234")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)