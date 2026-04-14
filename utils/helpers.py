# utils/helpers.py
from functools import wraps
from flask import session, jsonify
from datetime import datetime

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def format_timestamp(timestamp):
    """Format datetime object to string"""
    if isinstance(timestamp, datetime):
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp

def validate_violation_data(data):
    """Validate violation data before logging"""
    required_fields = ['employee_id', 'type']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    valid_types = ['No Cap', 'No Gloves', 'Surface Cleanliness Issue']
    if data['type'] not in valid_types:
        return False, f"Invalid violation type. Must be one of: {', '.join(valid_types)}"
    
    valid_severities = ['low', 'medium', 'high']
    if data.get('severity') and data['severity'] not in valid_severities:
        return False, f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
    
    return True, "Valid"