# routes/api.py
from flask import Blueprint, request, jsonify, session
from models.database import Database
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')
db = Database()

@api_bp.route('/log-violation', methods=['POST'])
def log_violation():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    employee_id = data.get('employee_id')
    violation_type = data.get('type')
    severity = data.get('severity', 'medium')
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO violations (employee_id, type, severity, timestamp) VALUES (%s, %s, %s, NOW())",
            (employee_id, violation_type, severity)
        )
        conn.commit()
        violation_id = cursor.lastrowid
    
    return jsonify({'success': True, 'violation_id': violation_id})

@api_bp.route('/get-violations')
def get_violations():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    with db.get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT v.*, e.name as employee_name, e.department 
            FROM violations v
            JOIN employees e ON v.employee_id = e.employee_id
            ORDER BY v.timestamp DESC
            LIMIT 100
        """)
        violations = cursor.fetchall()
    
    # Convert datetime objects to strings
    for v in violations:
        if v['timestamp']:
            v['timestamp'] = v['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify(violations)

@api_bp.route('/get-stats')
def get_stats():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    with db.get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM violations")
        total = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM violations 
            GROUP BY type
        """)
        by_type = cursor.fetchall()
        
        cursor.execute("""
            SELECT COUNT(*) as today 
            FROM violations 
            WHERE DATE(timestamp) = CURDATE()
        """)
        today = cursor.fetchone()['today']
        
        cursor.execute("""
            SELECT e.name, COUNT(*) as violation_count
            FROM violations v
            JOIN employees e ON v.employee_id = e.employee_id
            GROUP BY v.employee_id
            ORDER BY violation_count DESC
            LIMIT 10
        """)
        employee_ranking = cursor.fetchall()
    
    return jsonify({
        'total': total,
        'today': today,
        'by_type': by_type,
        'employee_ranking': employee_ranking
    })