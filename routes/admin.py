# routes/admin.py
from flask import Blueprint, render_template, jsonify
from functools import wraps
from flask import session
from models.database import Database

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
db = Database()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/monitor')
@admin_required
def monitor():
    return render_template('admin/monitor.html')