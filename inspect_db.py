import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'backend1', 'data_governance.db')
print(f"Checking database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(reports)")
    columns = cursor.fetchall()
    
    print("\nColumns in 'reports' table:")
    found = False
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
        if col[1] == 'file_path':
            found = True
            
    if found:
        print("\n✅ SUCCESS: 'file_path' column FOUND.")
    else:
        print("\n❌ FAILURE: 'file_path' column NOT FOUND.")
        
    conn.close()
except Exception as e:
    print(f"\nError: {e}")
