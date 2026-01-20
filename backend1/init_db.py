"""
Initialize the database by creating all tables
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend1.app import create_app, db

app = create_app()

with app.app_context():
    # Import models to register them
    from backend1.app.models import user, report
    
    # Create all tables
    db.create_all()
    print("✅ Database tables created successfully!")
    print("📊 Tables: users, reports")
