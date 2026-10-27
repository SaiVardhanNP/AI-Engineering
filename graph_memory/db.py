from pathlib import Path

import kuzu

DB_PATH = Path(__file__).parent / "data" / "graph.kuzu"


def get_connection(db_path: Path = DB_PATH) -> kuzu.Connection:
    """Open (or create) the on-disk graph DB and make sure the schema exists."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = kuzu.Database(str(db_path))
    conn = kuzu.Connection(db)
    init_schema(conn)
    return conn


def init_schema(conn: kuzu.Connection) -> None:
    # IF NOT EXISTS makes this safe to run on every startup.
    conn.execute("CREATE NODE TABLE IF NOT EXISTS Entity(name STRING PRIMARY KEY)")
    conn.execute(
        "CREATE REL TABLE IF NOT EXISTS PREFERS(FROM Entity TO Entity, since TIMESTAMP)"
    )
    conn.execute(
        "CREATE REL TABLE IF NOT EXISTS REJECTS(FROM Entity TO Entity, since TIMESTAMP)"
    )
