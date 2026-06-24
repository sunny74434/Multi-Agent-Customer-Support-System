import sqlite3
import uuid
from datetime import datetime

DB_PATH = "tickets.db"

# ── Create table on first run ──────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id         TEXT PRIMARY KEY,
            timestamp  TEXT,
            query      TEXT,
            category   TEXT,
            sentiment  TEXT,
            response   TEXT,
            status     TEXT DEFAULT 'open'
        )
    """)
    conn.commit()
    conn.close()

# ── Save a new ticket ──────────────────────────────────────────────
def save_ticket(query: str, category: str, sentiment: str,
                response: str, status: str = "open") -> str:
    ticket_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ticket_id, timestamp, query, category, sentiment, response, status)
    )
    conn.commit()
    conn.close()
    return ticket_id

# ── Fetch all tickets ──────────────────────────────────────────────
def get_all_tickets() -> list[dict]:
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT id, timestamp, query, category, sentiment, status "
        "FROM tickets ORDER BY timestamp DESC"
    )
    tickets = [
        {"id": r[0], "timestamp": r[1], "query": r[2],
         "category": r[3], "sentiment": r[4], "status": r[5]}
        for r in cursor.fetchall()
    ]
    conn.close()
    return tickets

# ── Update ticket status ───────────────────────────────────────────
def update_ticket_status(ticket_id: str, status: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE tickets SET status=? WHERE id=?", (status, ticket_id))
    conn.commit()
    conn.close()

init_db()