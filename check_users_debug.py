import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'backend1', 'data_governance.db')
print(f"Checking database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, role, is_active FROM users")
    users = cursor.fetchall()
    
    print(f"\nTotal users: {len(users)}")
    print(f"{'ID':<4} | {'Username':<15} | {'Role':<20} | {'Active':<6}")
    print("-" * 55)
    for user in users:
        print(f"{user['id']:<4} | {user['username']:<15} | {user['role']:<20} | {user['is_active']:<6}")
        
    conn.close()
except Exception as e:
    print(f"\nError: {e}")
