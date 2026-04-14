# routes/__init__.py
from .auth import auth_bp
from .admin import admin_bp
from .employee import employee_bp
from .api import api_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(api_bp)