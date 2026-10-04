import uuid
from datetime import datetime, timedelta, timezone

from database import get_connection

# After this long without a message, the next one starts a fresh conversation.
IDLE_HOURS = 4


class ConversationNotFound(Exception):
    """The conversation does not exist, or it belongs to a different customer."""


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def _turn(row):
    return {
        "ticket_id": row["id"],
        "message": row["message"],
        "reply": row["reply"],
        "status": row["status"],
        "review": row["review"],
        "human_reply": row["human_reply"],
        "created_at": row["created_at"],
    }


class ConversationStore:
    """A conversation is a thread of tickets. Each ticket already holds the
    customer's message and the reply they were shown, so the thread is rebuilt
    from tickets and no separate messages table is needed.
    """

    def resolve(self, conversation_id, customer_id, now=None):
        """Return the conversation id to use for a new message.

        No id starts a new conversation. An unknown id, or one that belongs to
        another customer, raises ConversationNotFound. A conversation that has
        been idle for IDLE_HOURS is left behind and a new one is started.
        """
        now = now or _now()

        if conversation_id is None:
            return self._create(customer_id, now)

        with get_connection() as connection:
            row = connection.execute(
                "SELECT customer_id, updated_at FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()

        if row is None or row["customer_id"] != customer_id:
            raise ConversationNotFound(conversation_id)

        last_activity = datetime.fromisoformat(row["updated_at"])
        if now - last_activity > timedelta(hours=IDLE_HOURS):
            return self._create(customer_id, now)

        return conversation_id

    def _create(self, customer_id, now):
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"

        with get_connection() as connection:
            connection.execute(
                "INSERT INTO conversations (id, customer_id, created_at, updated_at) VALUES (?,?,?,?)",
                (conversation_id, customer_id, now.isoformat(), now.isoformat()),
            )

        return conversation_id

    def touch(self, conversation_id):
        with get_connection() as connection:
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (_now().isoformat(), conversation_id),
            )

    def history(self, conversation_id, max_turns=3):
        """The most recent turns, oldest first, for the agents to read."""
        with get_connection() as connection:
            rows = connection.execute(
                """SELECT id, message, reply, status, review, human_reply, created_at
                   FROM tickets WHERE conversation_id = ?
                   ORDER BY created_at DESC, rowid DESC LIMIT ?""",
                (conversation_id, max_turns),
            ).fetchall()

        return [_turn(row) for row in reversed(rows)]

    def thread(self, conversation_id, customer_id=None):
        """Every turn, oldest first. With customer_id, only if it is theirs."""
        with get_connection() as connection:
            conversation = connection.execute(
                "SELECT customer_id FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()

            if conversation is None or (customer_id and conversation["customer_id"] != customer_id):
                raise ConversationNotFound(conversation_id)

            rows = connection.execute(
                """SELECT id, message, reply, status, review, human_reply, created_at
                   FROM tickets WHERE conversation_id = ?
                   ORDER BY created_at ASC, rowid ASC""",
                (conversation_id,),
            ).fetchall()

        return [_turn(row) for row in rows]
