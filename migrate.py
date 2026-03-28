import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'backend', 'instance', 'yly_hr.db')
if not os.path.exists(db_path):
    # Fallback for different CWD
    db_path = os.path.join(os.getcwd(), 'instance', 'yly_hr.db')

print(f"Connecting to {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE evaluation ADD COLUMN published BOOLEAN DEFAULT 0;")
    conn.commit()
    print("Column 'published' added successfully.")
except sqlite3.OperationalError as e:
    print(f"Error or column already exists: {e}")

conn.close()
