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
    import os
    # Configure static folder to serve client files
    client_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'client')
    app = Flask(__name__, static_folder=client_dir, static_url_path='')
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Enable CORS for all domains including file:// protocol (null origin)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": False
        }
    })
    
    # Disable strict slashes to prevent redirects that break CORS preflight
    app.url_map.strict_slashes = False
    
    # Register blueprints
    from backend1.app.routes import auth_bp, dashboard_bp, admin_bp, reports_bp
    from backend1.app.routes.companies import bp as companies_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(companies_bp)
    
    # Health check route
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'message': 'Data Governance Platform API is running',
            'version': '1.0.0',
            'author': 'Osman Yildiz'
        }, 200
    
    # API info endpoint
    @app.route('/api')
    def api_info():
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
                'reports': '/api/reports',
                'companies': '/api/companies'
            }
        }, 200
    
    # Serve client application
    @app.route('/')
    def index():
        from flask import send_from_directory
        return send_from_directory(app.static_folder, 'index.html')
    
    return app