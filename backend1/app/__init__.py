"""
Application factory and initialization
Author: Osman Yildiz
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from backend1.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    jwt.init_app(app)
    # Enable CORS for all domains on all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from backend1.app.routes import auth_bp, dashboard_bp, admin_bp, reports_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)
    
    # Health check route
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'message': 'Data Governance Platform API is running',
            'version': '1.0.0',
            'author': 'Osman Yildiz'
        }, 200
    
    # Welcome route
    @app.route('/')
    def index():
        return {
            'project': 'Data Governance & Compliance Platform',
            'author': 'Osman Yildiz',
            'institution': 'Walsh College',
            'endpoints': {
                'health': '/health',
                'register': '/api/auth/register',
                'login': '/api/auth/login',
                'dashboard': '/api/dashboard/overview',
                'admin': '/api/admin/users',
                'reports': '/api/reports'
            }
        }, 200
    
    return app