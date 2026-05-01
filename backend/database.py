import sqlite3
import os
from datetime import datetime

DB_FILE = "history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            total_transactions INTEGER,
            total_debits REAL,
            total_credits REAL,
            anomalies_count INTEGER,
            is_valid BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def log_processing(filename, total_transactions, total_debits, total_credits, anomalies_count, is_valid):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO processing_history 
        (filename, timestamp, total_transactions, total_debits, total_credits, anomalies_count, is_valid)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename,
        datetime.now().isoformat(),
        total_transactions,
        total_debits,
        total_credits,
        anomalies_count,
        is_valid
    ))
    conn.commit()
    conn.close()

def get_processing_history():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # To return dict-like objects
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM processing_history 
        ORDER BY timestamp DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
