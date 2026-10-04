import os
import sqlite3
from pathlib import Path

# SUPPORT_DB_PATH lets tests and deployments point at a different file
DB_PATH = Path(os.environ.get("SUPPORT_DB_PATH") or Path(__file__).resolve().parent / "data" / "support.db")

SCHEMA = """
CREATE TABLE customers (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE subscriptions (
    id                 TEXT PRIMARY KEY,
    customer_id        TEXT NOT NULL REFERENCES customers(id),
    plan               TEXT NOT NULL,   -- free | pro | team
    status             TEXT NOT NULL,   -- active | inactive | past_due | canceled
    started_at         TEXT NOT NULL,
    current_period_end TEXT
);

CREATE TABLE invoices (
    id              TEXT PRIMARY KEY,
    customer_id     TEXT NOT NULL REFERENCES customers(id),
    subscription_id TEXT NOT NULL REFERENCES subscriptions(id),
    amount_cents    INTEGER NOT NULL,
    status          TEXT NOT NULL,      -- paid | open | void
    period_start    TEXT NOT NULL,
    period_end      TEXT NOT NULL,
    created_at      TEXT NOT NULL
);

CREATE TABLE payments (
    id           TEXT PRIMARY KEY,
    customer_id  TEXT NOT NULL REFERENCES customers(id),
    invoice_id   TEXT REFERENCES invoices(id),
    amount_cents INTEGER NOT NULL,
    currency     TEXT NOT NULL,
    status       TEXT NOT NULL,         -- succeeded | failed | refunded
    failure_code TEXT,
    created_at   TEXT NOT NULL
);

CREATE TABLE error_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    occurred_at TEXT NOT NULL,
    service     TEXT NOT NULL,          -- auth | api | storage
    code        TEXT NOT NULL,
    message     TEXT NOT NULL
);

CREATE TABLE known_issues (
    id         TEXT PRIMARY KEY,
    title      TEXT NOT NULL,
    symptom    TEXT NOT NULL,
    status     TEXT NOT NULL,           -- investigating | resolved
    workaround TEXT
);
"""


# Created separately from SCHEMA so an existing database gets it without being re-seeded.
TICKETS_SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id                TEXT PRIMARY KEY,
    customer_id       TEXT NOT NULL REFERENCES customers(id),
    message           TEXT NOT NULL,
    status            TEXT NOT NULL,                -- replied | escalated
    review            TEXT NOT NULL DEFAULT 'none', -- none | open | resolved
    reply             TEXT,                         -- what the customer was shown
    draft             TEXT,                         -- the AI's last draft
    categories        TEXT NOT NULL,                -- json list
    findings          TEXT,                         -- the specialists' findings
    attempts          TEXT,                         -- json: each draft and its problems
    claims            TEXT,                         -- json: claims with supporting quotes
    timings           TEXT,                         -- json
    escalation_reason TEXT,
    human_reply       TEXT,
    created_at        TEXT NOT NULL,
    resolved_at       TEXT
);
"""


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


CONVERSATIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id          TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
"""


def ensure_tables():
    """Create tables and columns that are missing, keeping all existing data."""
    with get_connection() as connection:
        connection.executescript(TICKETS_SCHEMA)
        connection.executescript(CONVERSATIONS_SCHEMA)

        # a ticket belongs to a conversation. Older databases lack the column.
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(tickets)")}
        if "conversation_id" not in columns:
            connection.execute("ALTER TABLE tickets ADD COLUMN conversation_id TEXT")

        connection.execute("CREATE INDEX IF NOT EXISTS idx_tickets_conversation ON tickets(conversation_id)")


def init_db():
    """Create a fresh database. Any existing support.db is replaced."""
    DB_PATH.unlink(missing_ok=True)

    with get_connection() as connection:
        connection.executescript(SCHEMA)

    ensure_tables()
