import sqlite3
import os
from werkzeug.security import generate_password_hash

db_path = os.path.join(os.getcwd(), 'backend1', 'data_governance.db')
print(f"Seeding database at: {db_path}")

test_users = [
    ('admin_v2', 'admin_v2@example.com', 'admin', 'Admin', 'V2'),
    ('compliance_v2', 'compliance_v2@example.com', 'compliance officer', 'Compliance', 'Officer'),
    ('steward_v2', 'steward_v2@example.com', 'data steward', 'Data', 'Steward'),
    ('viewer_v2', 'viewer_v2@example.com', 'viewer', 'Global', 'Viewer'),
    ('user_v2', 'user_v2@example.com', 'user', 'Standard', 'User'),
]

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    password_hash = generate_password_hash('password123')
    
    for username, email, role, first_name, last_name in test_users:
        # Check if user exists by username or email
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            print(f"Skipping/Updating user: {username}")
            cursor.execute("UPDATE users SET role = ?, email = ?, first_name = ?, last_name = ? WHERE username = ?",
                          (role, email, first_name, last_name, username))
        else:
            print(f"Creating user: {username}")
            cursor.execute("INSERT INTO users (username, email, password_hash, role, first_name, last_name, is_active) VALUES (?, ?, ?, ?, ?, ?, 1)",
                          (username, email, password_hash, role, first_name, last_name))
            
    conn.commit()
    conn.close()
    print("✅ SUCCESS: Test users v2 seeded.")
except Exception as e:
    print(f"\nError: {e}")
