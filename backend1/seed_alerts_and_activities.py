"""
Seed Alerts and Activities for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend1.app import create_app, db
from backend1.app.models.user import User
from backend1.app.models.alert import Alert
from backend1.app.models.activity import Activity
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Get an admin user
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("❌ No admin user found. Run seed_data.py first.")
        sys.exit(1)
        
    print(f"🌱 Seeding for user: {admin.username}")
    
    # Add some alerts
    alerts = [
        Alert(
            user_id=admin.id,
            alert_type='compliance',
            severity='high',
            message='ISO 27001 compliance gap detected in Cloud Infrastructure.',
            created_at=datetime.utcnow() - timedelta(hours=2)
        ),
        Alert(
            user_id=admin.id,
            alert_type='access',
            severity='medium',
            message='Multiple failed login attempts from unknown IP: 192.168.1.45',
            created_at=datetime.utcnow() - timedelta(hours=5)
        ),
        Alert(
            user_id=None, # System-wide
            alert_type='system',
            severity='low',
            message='Platform maintenance scheduled for Sunday at 02:00 UTC.',
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
        Alert(
            user_id=admin.id,
            alert_type='compliance',
            severity='critical',
            message='Critical Policy Exception: Privacy Policy has expired for 3 vendors.',
            created_at=datetime.utcnow() - timedelta(minutes=15)
        )
    ]
    
    db.session.add_all(alerts)
    
    # Add some activities
    activities = [
        Activity(
            user_id=admin.id,
            action='login',
            description='Admin logged in successfully',
            created_at=datetime.utcnow() - timedelta(minutes=45)
        ),
        Activity(
            user_id=admin.id,
            action='approve_report',
            description='Approved "Q4 Security Audit" for Apple Inc.',
            created_at=datetime.utcnow() - timedelta(hours=1)
        ),
        Activity(
            user_id=admin.id,
            action='export_reports',
            description='Exported compliance summary to PDF',
            created_at=datetime.utcnow() - timedelta(hours=3)
        ),
        Activity(
            user_id=admin.id,
            action='deactivate_user',
            description='Deactivated user "test_viewer_1"',
            created_at=datetime.utcnow() - timedelta(days=2)
        )
    ]
    
    db.session.add_all(activities)
    db.session.commit()
    
    print("✅ Successfully seeded 4 alerts and 4 activities!")
