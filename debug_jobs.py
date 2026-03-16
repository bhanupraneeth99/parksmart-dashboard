import sqlite3
import os

db_path = os.path.join("backend", "parksmart.db")
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, job_id, video_name, status FROM processing_jobs ORDER BY id DESC LIMIT 5;")
        rows = cursor.fetchall()
        print("ID | Job ID | Video Name | Status")
        print("-" * 50)
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
