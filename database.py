import sqlite3
from datetime import datetime
from contextlib import closing

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

# The filename for the SQLite database
DB_NAME = "review_booster.db"

# ==========================================
# 2. DATABASE OPERATIONS
# ==========================================

def init_db():
    """
    Initializes the database by creating the 'invitations' table 
    if it does not already exist.
    """
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER DEFAULT 1,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                review_url TEXT,
                status TEXT NOT NULL,
                twilio_sid TEXT,
                timestamp TEXT NOT NULL,
                is_sinpe INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

def log_invitation(business_id, name, phone, url, status, is_sinpe, sid=None):
    """
    Inserts a new record into the 'invitations' table.
    
    Parameters:
    - business_id: ID of the business (default 1).
    - name: Name of the customer.
    - phone: Customer's phone number.
    - url: The review link sent.
    - status: 'Success' or 'Failed' status of the message.
    - is_sinpe: Boolean indicating if payment was via SINPE (stored as 0 or 1).
    - sid: The Twilio SID for tracking the message (optional).
    """
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.execute('''
            INSERT INTO invitations (
                business_id, customer_name, customer_phone, review_url, 
                status, twilio_sid, timestamp, is_sinpe
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            business_id, 
            name, 
            phone, 
            url, 
            status, 
            sid, 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            int(is_sinpe)
        ))
        conn.commit()

def get_all_invitations(business_id):
    """
    Retrieves all invitation records for a specific business, 
    sorted by the most recent timestamp first.
    
    Returns a list of dictionaries for easier frontend processing.
    """
    with closing(sqlite3.connect(DB_NAME)) as conn:
        # Enable row access by column name
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM invitations WHERE business_id = ? ORDER BY timestamp DESC", 
            (business_id,)
        ).fetchall()
        
        # Convert sqlite3.Row objects to dictionaries
        return [dict(row) for row in rows]