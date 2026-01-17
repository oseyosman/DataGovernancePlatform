import sys
import os
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend1.app import create_app, db
from backend1.app.models.user import User

app = create_app()

print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        # Create tables if they don't exist (fallback)
        db.create_all()
        print("Tables checked/created.")

        # Check if admin exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created admin user")
        else:
             print("Admin user already exists")

        # Check if regular user exists
        if not User.query.filter_by(username='user').first():
            user = User(username='user', email='user@example.com', role='user')
            user.set_password('user123')
            db.session.add(user)
            print("Created regular user")
        else:
            print("Regular user already exists")
        
        db.session.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print("Error seeding database:")
        traceback.print_exc()
