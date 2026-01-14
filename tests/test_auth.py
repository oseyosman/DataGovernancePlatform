"""
Authentication tests

Author: Osman Yildiz
"""
import pytest
from app import create_app, db
from app.models.user import User
from config import TestingConfig

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_register_user(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!',
        'role': 'viewer'
    })
    assert response.status_code == 201
    assert 'user' in response.json

def test_login_user(client):
    """Test user login"""
    # First register
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!',
        'role': 'viewer'
    })
    
    # Then login
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'Test123!'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json