import json
import uuid
from datetime import datetime, timezone

from database import get_connection

_JSON_COLUMNS = ("categories", "attempts", "claims", "timings")


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class TicketStore:
    """Persists every handled ticket so the support team can review it later."""

    def save(self, result, customer_id, message, customer_reply, conversation_id=None):
        """Store one finished pipeline run and return its ticket id.

        customer_reply is the text the customer was actually shown, which for an
        escalation is the fixed handoff message and not the AI's draft.
        """
        replied = result["status"] == "reply"
        attempts = result.get("attempts", [])
        claims = attempts[-1].get("claims", []) if attempts else []
        ticket_id = f"tkt_{uuid.uuid4().hex[:8]}"

        with get_connection() as connection:
            connection.execute(
                """INSERT INTO tickets
                   (id, customer_id, message, status, review, reply, draft, categories,
                    findings, attempts, claims, timings, escalation_reason, created_at,
                    conversation_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    ticket_id,
                    customer_id,
                    message,
                    "replied" if replied else "escalated",
                    # an answered ticket still needs a person when the assistant said so
                    "open" if (not replied or result.get("needs_human")) else "none",
                    customer_reply,
                    None if replied else result.get("last_draft"),
                    json.dumps(result.get("classification", {}).get("categories", [])),
                    result.get("findings"),
                    json.dumps(attempts),
                    json.dumps(claims),
                    json.dumps(result.get("timings", {})),
                    result.get("needs_human") if replied else result.get("reason"),
                    _now(),
                    conversation_id,
                ),
            )

        return ticket_id

    def list(self, status=None, limit=50):
        sql = """SELECT t.id, t.customer_id, c.name AS customer_name, t.message, t.status,
                        t.review, t.categories, t.escalation_reason, t.created_at,
                        t.conversation_id,
                        CASE WHEN t.conversation_id IS NULL THEN 1 ELSE
                          (SELECT COUNT(*) FROM tickets x WHERE x.conversation_id = t.conversation_id)
                        END AS message_count
                 FROM tickets t JOIN customers c ON c.id = t.customer_id"""
        params = []

        if status:
            sql += " WHERE t.status = ?"
            params.append(status)

        sql += " ORDER BY t.created_at DESC, t.rowid DESC LIMIT ?"
        params.append(limit)

        with get_connection() as connection:
            rows = [dict(row) for row in connection.execute(sql, params)]

        for row in rows:
            row["categories"] = json.loads(row["categories"])

        return rows

    def get(self, ticket_id):
        with get_connection() as connection:
            row = connection.execute(
                """SELECT t.*, c.name AS customer_name
                   FROM tickets t JOIN customers c ON c.id = t.customer_id
                   WHERE t.id = ?""",
                (ticket_id,),
            ).fetchone()

        if row is None:
            return None

        ticket = dict(row)
        for column in _JSON_COLUMNS:
            ticket[column] = json.loads(ticket[column]) if ticket[column] else None

        return ticket

    def resolve(self, ticket_id, human_reply):
        """Record a human's reply on an open escalation. Returns False if there is none to resolve."""
        with get_connection() as connection:
            cursor = connection.execute(
                """UPDATE tickets SET review = 'resolved', human_reply = ?, resolved_at = ?
                   WHERE id = ? AND review = 'open'""",
                (human_reply, _now(), ticket_id),
            )

        return cursor.rowcount == 1
