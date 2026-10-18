import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'backend1', 'data_governance.db')
print(f"Updating database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Update oseyosman to admin
    cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'oseyosman'")
    
    if cursor.rowcount > 0:
        print("✅ SUCCESS: User 'oseyosman' promoted to admin.")
    else:
        # Try 'oseyos' just in case the print was truncated
        cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'oseyos'")
        if cursor.rowcount > 0:
            print("✅ SUCCESS: User 'oseyos' promoted to admin.")
        else:
            print("❌ FAILURE: No user found with username 'oseyosman' or 'oseyos'.")
            
    conn.commit()
    conn.close()
except Exception as e:
    print(f"\nError: {e}")
