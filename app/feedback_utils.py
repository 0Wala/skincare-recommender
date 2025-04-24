import sqlite3
import datetime

DB_PATH = "app/feedback.db"

def insert_feedback(message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO feedback (message, submitted_at) VALUES (?, ?)",
        (message, timestamp)
    )
    conn.commit()
    conn.close()

def get_all_feedback():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, message, submitted_at FROM feedback")
    rows = cursor.fetchall()
    conn.close()
    return rows
