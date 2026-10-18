import sqlite3
import os

# Database path
# Database path
# Try to find the instance folder
current_dir = os.getcwd()
possible_paths = [
    os.path.join(current_dir, 'backend1', 'instance', 'data_governance.db'),
    os.path.join(current_dir, 'instance', 'data_governance.db'),
    os.path.join(current_dir, 'data_governance.db'),
    os.path.join(current_dir, 'backend1', 'data_governance.db')
]

db_path = None
for path in possible_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    # If not found, default to creating it in backend1/instance
    db_path = os.path.join(current_dir, 'backend1', 'instance', 'data_governance.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    print(f"Database not found. Creating new at {db_path}")

print(f"Using database: {db_path}")

# SQL file paths
schema_file = os.path.join('backend1', 'database', 'schema.sql')
seed_file = os.path.join('backend1', 'database', 'seed_db.sql')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Run schema.sql
    if os.path.exists(schema_file):
        print(f"Running schema.sql...")
        with open(schema_file, 'r') as f:
            schema_script = f.read()
        cursor.executescript(schema_script)
        print("Schema applied.")
    else:
        print(f"Schema file not found at {schema_file}")

    # Run seed_db.sql
    if os.path.exists(seed_file):
        print(f"Running seed_db.sql...")
        with open(seed_file, 'r') as f:
            seed_script = f.read()
        cursor.executescript(seed_script)
        print("Seed data applied.")
    else:
        print(f"Seed file not found at {seed_file}")

    conn.commit()
    conn.close()
    print("Database setup complete.")

except Exception as e:
    print(f"Error executing SQL: {e}")
