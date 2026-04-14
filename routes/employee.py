# routes/employee.py
from flask import Blueprint, render_template, session, jsonify
from functools import wraps

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@employee_bp.route('/camera')
@login_required
def camera():
    if session.get('role') != 'employee':
        return jsonify({'error': 'Access denied'}), 403
    return render_template('employee/camera.html', 
                         employee_name=session.get('name'),
                         employee_id=session.get('employee_id'))