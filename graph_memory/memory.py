from datetime import datetime

import kuzu


def remember_preference(
    conn: kuzu.Connection, user: str, preferred: str, over: str
) -> None:
    """Store "user prefers `preferred` over `over`" as two edges."""
    now = datetime.now()

    # 1. Make sure all three nodes exist (MERGE = find or create, no duplicates).
    for name in (user, preferred, over):
        conn.execute("MERGE (e:Entity {name: $name})", {"name": name})

    # 2. Delete facts this statement contradicts:
    #    - user used to reject `preferred`
    #    - user used to prefer `over`
    conn.execute(
        "MATCH (a:Entity {name: $user})-[r:REJECTS]->(b:Entity {name:$preferred}) DELETE r",
        {"user": user, "preferred": preferred},
    )
    conn.execute(
        "MATCH (a:Entity {name: $user})-[r:PREFERS]->(b:Entity {name:$over}) DELETE r",
        {"user": user, "over": over},
    )

    # 3. Create the PREFERS edge (MERGE so repeating the fact adds nothing).
    conn.execute(
        "MATCH (u:Entity {name: $user}), (p:Entity {name: $preferred}) "
        "MERGE (u)-[r:PREFERS]->(p) "
        "ON CREATE SET r.since = $now",
        {"user": user, "preferred": preferred, "now": now},
    )

    # 4. Create the REJECTS edge from user to `over`, same pattern as above.
    conn.execute(
        "MATCH (a:Entity {name: $user}), (b:Entity {name: $over}) "
        "MERGE (a)-[r:REJECTS]->(b) "
        "ON CREATE SET r.since = $now",
        {"user": user, "over": over, "now": now},
    )


def get_preferred(conn: kuzu.Connection, user: str) -> list[str]:
    result = conn.execute(
        "MATCH (u:Entity {name: $user})-[r:PREFERS]->(x:Entity) "
        "RETURN x.name ORDER BY r.since DESC",
        {"user": user},
    )
    names = []
    while result.has_next():
        names.append(result.get_next()[0])
    return names


def get_rejected(conn: kuzu.Connection, user: str) -> list[str]:
    result = conn.execute(
        "MATCH (u:Entity {name: $user})-[r:REJECTS]->(x:Entity) "
        "RETURN x.name ORDER BY r.since DESC",
        {"user": user},
    )
    names = []
    while result.has_next():
        names.append(result.get_next()[0])
    return names


def describe(user: str, verb: str, items: list[str]) -> str:
    if not items:
        return ""
    return f"{user} {verb}: {', '.join(items)}."


def preferences_as_text(conn: kuzu.Connection, user: str) -> str:
    """Summarise what `user` prefers and rejects as one sentence for the agent."""
    preferred_description = describe(user, "prefers", get_preferred(conn, user))
    rejected_description = describe(user, "rejects", get_rejected(conn, user))

    clauses = [c for c in (preferred_description, rejected_description) if c]
    if not clauses:
        return f"No stored preferences for {user}."
    return " ".join(clauses)
