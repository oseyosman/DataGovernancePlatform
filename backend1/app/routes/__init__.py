"""
Routes package initialization
"""
from backend1.app.routes.auth import bp as auth_bp
from backend1.app.routes.dashboard import bp as dashboard_bp
from backend1.app.routes.admin import bp as admin_bp
from backend1.app.routes.reports import bp as reports_bp

__all__ = ['auth_bp', 'dashboard_bp', 'admin_bp', 'reports_bp']