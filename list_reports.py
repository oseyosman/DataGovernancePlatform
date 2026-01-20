import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'backend1', 'data_governance.db')
print(f"Checking reports in: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List Users
    print("\n--- USERS ---")
    cursor.execute("SELECT id, username, role FROM users")
    for row in cursor.fetchall():
        print(row)
        
    # List Reports
    print("\n--- REPORTS ---")
    cursor.execute("SELECT id, title, created_by, file_path FROM reports")
    reports = cursor.fetchall()
    if not reports:
        print("No reports found.")
    for row in reports:
        print(row)
            
    conn.close()
except Exception as e:
    print(f"\nError: {e}")
