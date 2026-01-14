"""
Application factory and initialization
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from backproject.config import Config

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
    CORS(app)
    
    # Register blueprints
    from app.routes import auth, dashboard
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    
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
                'dashboard': '/api/dashboard/overview'
            }
        }, 200
    
    return app