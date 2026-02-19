"""
Security Test Suite — Data Governance & Compliance Platform
Author: Osman Yildiz
Walsh College — MSIT Capstone Project

Tests cover all 8 security areas:
1. SQL Injection
2. XSS Protection
3. CSRF Protection
4. Authentication Bypass
5. JWT Token Security
6. Sensitive Data Exposure
7. Password Hashing Strength
8. HTTPS Readiness
"""
import sys
import os
import pytest
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend1.app import create_app, db
from backend1.app.models.user import User
from backend1.config import TestingConfig


# ─── Fixtures ───────────────────────────────────────────────────────────

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


@pytest.fixture
def registered_user(client):
    """Register and return a standard user with credentials"""
    creds = {
        'username': 'securitytester',
        'email': 'security@test.com',
        'password': 'SecurePass1!',
        'first_name': 'Security',
        'last_name': 'Tester'
    }
    client.post('/api/auth/register', json=creds)
    return creds


@pytest.fixture
def auth_token(client, registered_user):
    """Get a valid JWT access token"""
    resp = client.post('/api/auth/login', json={
        'username': registered_user['username'],
        'password': registered_user['password']
    })
    return resp.json['access_token']


# ═══════════════════════════════════════════════════════════════════════
# 1. SQL INJECTION TESTING
# ═══════════════════════════════════════════════════════════════════════

class TestSQLInjection:
    """Test that SQL injection payloads are safely handled"""

    SQL_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "1; DELETE FROM users",
        "admin'--",
        "' OR 1=1 --",
    ]

    def test_login_sql_injection(self, client, registered_user):
        """SQL injection via login username/password should fail authentication"""
        for payload in self.SQL_PAYLOADS:
            resp = client.post('/api/auth/login', json={
                'username': payload,
                'password': payload
            })
            assert resp.status_code == 401, \
                f"SQL injection payload should not authenticate: {payload}"

    def test_register_sql_injection(self, client):
        """SQL injection via registration fields should not break the app"""
        for payload in self.SQL_PAYLOADS:
            resp = client.post('/api/auth/register', json={
                'username': payload,
                'email': f'{payload}@test.com',
                'password': 'SecurePass1!',
                'first_name': payload,
                'last_name': payload
            })
            # Should return 201 (created) or 400 (validation error), never 500
            assert resp.status_code in (201, 400), \
                f"SQL injection should not cause server error: {payload}"

    def test_company_search_sql_injection(self, client, auth_token):
        """SQL injection via company search parameter"""
        for payload in self.SQL_PAYLOADS:
            resp = client.get(
                f'/api/companies/?search={payload}',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            assert resp.status_code in (200, 400), \
                f"Search SQL injection should not cause server error: {payload}"


# ═══════════════════════════════════════════════════════════════════════
# 2. XSS PROTECTION VALIDATION
# ═══════════════════════════════════════════════════════════════════════

class TestXSSProtection:
    """Test Cross-Site Scripting protections"""

    XSS_PAYLOADS = [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        '"><script>alert(1)</script>',
        "javascript:alert('XSS')",
        '<svg onload=alert(1)>',
    ]

    def test_register_xss_stored(self, client):
        """XSS payloads stored via registration should be inert in JSON responses"""
        for i, payload in enumerate(self.XSS_PAYLOADS):
            resp = client.post('/api/auth/register', json={
                'username': f'xssuser{i}',
                'email': f'xss{i}@test.com',
                'password': 'SecurePass1!',
                'first_name': payload,
                'last_name': payload
            })
            if resp.status_code == 201:
                # Verify response is JSON (Content-Type prevents browser execution)
                assert 'application/json' in resp.content_type
                # If data is returned, the script tag should be stored as-is
                # (it won't execute because Content-Type is application/json)
                user_data = resp.json.get('user', {})
                assert user_data.get('first_name') == payload, \
                    "Data should be stored as-is (JSON Content-Type prevents XSS)"

    def test_json_content_type_headers(self, client, auth_token):
        """All API responses should have application/json Content-Type"""
        endpoints = [
            '/health',
            '/api',
        ]
        for endpoint in endpoints:
            resp = client.get(endpoint)
            assert 'application/json' in resp.content_type, \
                f"Endpoint {endpoint} should return JSON Content-Type"

    def test_security_headers_present(self, client):
        """X-XSS-Protection header should be set"""
        resp = client.get('/health')
        assert resp.headers.get('X-XSS-Protection') == '1; mode=block', \
            "X-XSS-Protection header should be set"
        assert resp.headers.get('X-Content-Type-Options') == 'nosniff', \
            "X-Content-Type-Options: nosniff should be set"


# ═══════════════════════════════════════════════════════════════════════
# 3. CSRF PROTECTION
# ═══════════════════════════════════════════════════════════════════════

class TestCSRFProtection:
    """Test CSRF protection — JWT in Authorization header is inherently CSRF-safe"""

    def test_jwt_based_auth_is_csrf_safe(self, client, auth_token):
        """JWT tokens sent via Authorization header (not cookies) are CSRF-immune"""
        # Without Authorization header, protected endpoints should reject
        resp = client.get('/api/dashboard/overview')
        assert resp.status_code == 401, \
            "Protected endpoint should reject requests without JWT"

        # With Authorization header, it should work
        resp = client.get(
            '/api/dashboard/overview',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert resp.status_code == 200

    def test_no_session_cookies_used(self, client, registered_user):
        """Login should not set session cookies (JWT-only auth)"""
        resp = client.post('/api/auth/login', json={
            'username': registered_user['username'],
            'password': registered_user['password']
        })
        # Check that no session cookie is set
        cookies = resp.headers.getlist('Set-Cookie')
        session_cookies = [c for c in cookies if 'session' in c.lower()]
        assert len(session_cookies) == 0, \
            "Login should not set session cookies (pure JWT auth)"


# ═══════════════════════════════════════════════════════════════════════
# 4. AUTHENTICATION BYPASS TESTING
# ═══════════════════════════════════════════════════════════════════════

class TestAuthenticationBypass:
    """Test that authentication cannot be bypassed"""

    PROTECTED_ENDPOINTS = [
        ('GET', '/api/dashboard/overview'),
        ('GET', '/api/dashboard/stats'),
        ('GET', '/api/reports/'),
        ('GET', '/api/companies/'),
        ('GET', '/api/admin/users'),
        ('GET', '/api/admin/stats'),
    ]

    def test_no_token_rejected(self, client):
        """All protected endpoints should reject requests without JWT"""
        for method, url in self.PROTECTED_ENDPOINTS:
            if method == 'GET':
                resp = client.get(url)
            elif method == 'POST':
                resp = client.post(url, json={})
            assert resp.status_code == 401, \
                f"{method} {url} should return 401 without token"

    def test_invalid_token_rejected(self, client):
        """Malformed and fake tokens should be rejected"""
        fake_tokens = [
            'not-a-real-token',
            'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.fake_signature',
            '',
            'Bearer ',
        ]
        for token in fake_tokens:
            resp = client.get(
                '/api/dashboard/overview',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert resp.status_code in (401, 422), \
                f"Fake token should be rejected: {token[:30]}..."

    def test_privilege_escalation_blocked(self, client):
        """Registration should NOT accept role parameter (always defaults to 'user')"""
        resp = client.post('/api/auth/register', json={
            'username': 'escalation_test',
            'email': 'escalation@test.com',
            'password': 'SecurePass1!',
            'first_name': 'Escalation',
            'last_name': 'Test',
            'role': 'admin'  # Attempting privilege escalation
        })
        assert resp.status_code == 201
        user = resp.json['user']
        assert user['role'] == 'user', \
            "CRITICAL: Registration should ignore client-supplied role and default to 'user'"

    def test_admin_endpoints_require_admin_role(self, client, auth_token):
        """Non-admin users should be rejected from admin endpoints"""
        admin_endpoints = [
            ('GET', '/api/admin/users'),
            ('GET', '/api/admin/stats'),
        ]
        for method, url in admin_endpoints:
            resp = client.get(
                url,
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            assert resp.status_code == 403, \
                f"Non-admin should get 403 on {url}"


# ═══════════════════════════════════════════════════════════════════════
# 5. JWT TOKEN SECURITY & EXPIRATION
# ═══════════════════════════════════════════════════════════════════════

class TestJWTSecurity:
    """Test JWT token security configuration"""

    def test_token_contains_no_sensitive_data(self, client, registered_user):
        """JWT payload should not contain password or sensitive data"""
        import base64
        resp = client.post('/api/auth/login', json={
            'username': registered_user['username'],
            'password': registered_user['password']
        })
        token = resp.json['access_token']
        # Decode JWT payload (middle part)
        payload_b64 = token.split('.')[1]
        # Add padding
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.b64decode(payload_b64))

        assert 'password' not in str(payload).lower(), \
            "JWT payload should not contain password"
        assert registered_user['password'] not in str(payload), \
            "JWT payload should not contain raw password"

    def test_secret_key_not_hardcoded(self, app):
        """Secret keys should not be the known hardcoded development defaults"""
        assert app.config['SECRET_KEY'] != 'dev-secret-key-change-in-production', \
            "CRITICAL: SECRET_KEY is using the known hardcoded default"
        assert app.config['JWT_SECRET_KEY'] != 'jwt-secret-key-change-in-production', \
            "CRITICAL: JWT_SECRET_KEY is using the known hardcoded default"

    def test_token_expiration_configured(self, app):
        """JWT tokens should have reasonable expiration times"""
        from datetime import timedelta
        access_exp = app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
        refresh_exp = app.config.get('JWT_REFRESH_TOKEN_EXPIRES')

        assert access_exp is not None, "Access token expiration should be configured"
        assert refresh_exp is not None, "Refresh token expiration should be configured"

        # Access token should expire within 24 hours
        assert access_exp <= timedelta(hours=24), \
            "Access token expiration should be <= 24 hours"
        # Refresh token should expire within 90 days
        assert refresh_exp <= timedelta(days=90), \
            "Refresh token expiration should be <= 90 days"

    def test_refresh_token_flow(self, client, registered_user):
        """Refresh token should generate a new access token"""
        resp = client.post('/api/auth/login', json={
            'username': registered_user['username'],
            'password': registered_user['password']
        })
        refresh_token = resp.json['refresh_token']

        resp = client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        assert resp.status_code == 200
        assert 'access_token' in resp.json


# ═══════════════════════════════════════════════════════════════════════
# 6. SENSITIVE DATA EXPOSURE
# ═══════════════════════════════════════════════════════════════════════

class TestSensitiveDataExposure:
    """Test that sensitive data is not exposed in API responses"""

    def test_password_hash_not_in_response(self, client, registered_user):
        """User API responses should never contain password_hash"""
        resp = client.post('/api/auth/register', json={
            'username': 'exposure_test',
            'email': 'exposure@test.com',
            'password': 'SecurePass1!',
            'first_name': 'Test',
            'last_name': 'User'
        })
        response_str = json.dumps(resp.json)
        assert 'password_hash' not in response_str, \
            "password_hash should never appear in API response"
        assert 'pbkdf2' not in response_str and 'scrypt' not in response_str, \
            "Hash value should never appear in API response"

    def test_error_messages_are_generic(self, client):
        """500 errors should not expose internal details"""
        # Try to trigger an error with bad JSON
        resp = client.post('/api/auth/login',
                          data='not json',
                          content_type='application/json')
        if resp.status_code == 500:
            error_msg = resp.json.get('error', '')
            # Should NOT contain tracebacks, file paths, or SQL
            assert 'Traceback' not in error_msg
            assert 'File "' not in error_msg
            assert 'SELECT' not in error_msg.upper()

    def test_cors_not_wildcard(self, client):
        """CORS should not allow all origins"""
        resp = client.options('/api/auth/login', headers={
            'Origin': 'https://evil-site.com',
            'Access-Control-Request-Method': 'POST'
        })
        allow_origin = resp.headers.get('Access-Control-Allow-Origin', '')
        assert allow_origin != '*', \
            "CORS should not use wildcard '*' origin"

    def test_user_to_dict_excludes_password(self, app):
        """User.to_dict() should not include password_hash"""
        with app.app_context():
            user = User(
                username='dicttest',
                email='dict@test.com',
                first_name='Dict',
                last_name='Test',
                role='user'
            )
            user.set_password('SecurePass1!')
            user_dict = user.to_dict()
            assert 'password_hash' not in user_dict
            assert 'password' not in user_dict


# ═══════════════════════════════════════════════════════════════════════
# 7. PASSWORD HASHING STRENGTH
# ═══════════════════════════════════════════════════════════════════════

class TestPasswordHashing:
    """Test password hashing implementation"""

    def test_password_is_hashed_not_plaintext(self, app):
        """Stored password should be hashed, not plaintext"""
        with app.app_context():
            user = User(username='hashtest', email='hash@test.com',
                        first_name='Hash', last_name='Test', role='user')
            user.set_password('MyPlainPassword1!')
            assert user.password_hash != 'MyPlainPassword1!', \
                "Password should be hashed, not stored as plaintext"
            assert len(user.password_hash) > 50, \
                "Password hash should be a long string"

    def test_password_hash_uses_strong_algorithm(self, app):
        """Password hash should use scrypt or pbkdf2"""
        with app.app_context():
            user = User(username='algotest', email='algo@test.com',
                        first_name='Algo', last_name='Test', role='user')
            user.set_password('TestPassword1!')
            # Werkzeug uses scrypt (3.x+) or pbkdf2:sha256
            assert ('scrypt' in user.password_hash or
                    'pbkdf2:sha256' in user.password_hash), \
                f"Expected scrypt or pbkdf2:sha256, got: {user.password_hash[:30]}"

    def test_same_password_different_hashes(self, app):
        """Same password should produce different hashes (salting)"""
        with app.app_context():
            user1 = User(username='salt1', email='salt1@test.com',
                         first_name='S1', last_name='T', role='user')
            user2 = User(username='salt2', email='salt2@test.com',
                         first_name='S2', last_name='T', role='user')
            user1.set_password('SamePassword1!')
            user2.set_password('SamePassword1!')
            assert user1.password_hash != user2.password_hash, \
                "Same password should produce different hashes (unique salt)"

    def test_password_verification_works(self, app):
        """check_password should correctly verify passwords"""
        with app.app_context():
            user = User(username='verify', email='verify@test.com',
                        first_name='V', last_name='T', role='user')
            user.set_password('CorrectPassword1!')
            assert user.check_password('CorrectPassword1!') is True
            assert user.check_password('WrongPassword1!') is False

    def test_password_strength_policy_enforced(self, client):
        """Registration should enforce password strength requirements"""
        weak_passwords = [
            ('short', 'Ab1!'),                    # Too short
            ('no_upper', 'lowercase1!'),           # No uppercase
            ('no_lower', 'UPPERCASE1!'),           # No lowercase
            ('no_digit', 'NoDigitsHere!'),         # No digit
            ('no_special', 'NoSpecial123'),        # No special char
        ]
        for label, password in weak_passwords:
            resp = client.post('/api/auth/register', json={
                'username': f'weak_{label}',
                'email': f'weak_{label}@test.com',
                'password': password,
                'first_name': 'Weak',
                'last_name': 'Test'
            })
            assert resp.status_code == 400, \
                f"Weak password '{label}' should be rejected (got {resp.status_code})"


# ═══════════════════════════════════════════════════════════════════════
# 8. HTTPS READINESS
# ═══════════════════════════════════════════════════════════════════════

class TestHTTPSReadiness:
    """Test that the app is configured for HTTPS deployment"""

    def test_hsts_header_present(self, client):
        """Strict-Transport-Security header should be set"""
        resp = client.get('/health')
        hsts = resp.headers.get('Strict-Transport-Security')
        assert hsts is not None, \
            "HSTS header should be set for HTTPS readiness"
        assert 'max-age=' in hsts

    def test_x_frame_options_header(self, client):
        """X-Frame-Options should prevent clickjacking"""
        resp = client.get('/health')
        xfo = resp.headers.get('X-Frame-Options')
        assert xfo in ('DENY', 'SAMEORIGIN'), \
            "X-Frame-Options should be DENY or SAMEORIGIN"

    def test_content_security_policy_header(self, client):
        """Content-Security-Policy should be configured"""
        resp = client.get('/health')
        csp = resp.headers.get('Content-Security-Policy')
        assert csp is not None, \
            "Content-Security-Policy header should be set"
        assert "default-src" in csp

    def test_referrer_policy_header(self, client):
        """Referrer-Policy should be configured"""
        resp = client.get('/health')
        rp = resp.headers.get('Referrer-Policy')
        assert rp is not None, \
            "Referrer-Policy header should be set"

    def test_cache_control_header(self, client):
        """Cache-Control should prevent caching of API responses"""
        resp = client.get('/health')
        cc = resp.headers.get('Cache-Control')
        assert cc is not None and 'no-store' in cc, \
            "Cache-Control should include 'no-store'"

    def test_max_upload_size_configured(self, app):
        """File upload size should be limited"""
        max_size = app.config.get('MAX_CONTENT_LENGTH')
        assert max_size is not None, \
            "MAX_CONTENT_LENGTH should be configured"
        assert max_size <= 32 * 1024 * 1024, \
            "Max upload size should be reasonable (<=32MB)"
