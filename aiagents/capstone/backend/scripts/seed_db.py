import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import DB_PATH, get_connection, init_db

NOW = datetime.now(timezone.utc).replace(microsecond=0)


def ago(days=0, hours=0, minutes=0, seconds=0):
    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return (NOW - delta).isoformat()


def ahead(days):
    return (NOW + timedelta(days=days)).isoformat()


CUSTOMERS = [
    ("cus_001", "Alice Rao", "alice@example.com", ago(days=200)),
    ("cus_002", "Bob Mehta", "bob@example.com", ago(days=400)),
    ("cus_003", "Carol Singh", "carol@example.com", ago(days=90)),
    ("cus_004", "Dan Iyer", "dan@example.com", ago(days=150)),
    ("cus_005", "Eve Kapoor", "eve@example.com", ago(days=60)),
    ("cus_006", "Frank Nair", "frank@example.com", ago(days=300)),
]

SUBSCRIPTIONS = [
    # id, customer, plan, status, started, period_end
    ("sub_001", "cus_001", "pro", "inactive", ago(days=1), None),
    ("sub_002", "cus_002", "pro", "active", ago(days=400), ahead(12)),
    ("sub_003", "cus_003", "pro", "past_due", ago(days=90), ago(days=3)),
    ("sub_004", "cus_004", "pro", "active", ago(days=150), ahead(8)),
    ("sub_005", "cus_005", "pro", "active", ago(days=60), ahead(20)),
    ("sub_006", "cus_006", "pro", "active", ago(days=300), ahead(5)),
]

INVOICES = [
    # id, customer, subscription, amount, status, period_start, period_end, created
    ("inv_001", "cus_001", "sub_001", 2500, "paid", ago(days=1), ahead(29), ago(days=1)),
    ("inv_002", "cus_002", "sub_002", 2500, "paid", ago(days=18), ahead(12), ago(days=18)),
    ("inv_003", "cus_003", "sub_003", 2500, "open", ago(days=3), ahead(27), ago(days=3)),
    # overage: base plan plus compute and egress, so the total is above $25
    ("inv_004", "cus_004", "sub_004", 6140, "paid", ago(days=22), ahead(8), ago(days=22)),
    ("inv_005", "cus_005", "sub_005", 2500, "paid", ago(days=10), ahead(20), ago(days=10)),
    ("inv_006", "cus_006", "sub_006", 2500, "paid", ago(days=25), ahead(5), ago(days=25)),
]

PAYMENTS = [
    # id, customer, invoice, amount, currency, status, failure_code, created
    # cus_001: the same invoice was charged twice, 40 seconds apart
    ("pay_001a", "cus_001", "inv_001", 2500, "usd", "succeeded", None, ago(days=1, seconds=40)),
    ("pay_001b", "cus_001", "inv_001", 2500, "usd", "succeeded", None, ago(days=1)),
    # cus_002: healthy, a single charge
    ("pay_002", "cus_002", "inv_002", 2500, "usd", "succeeded", None, ago(days=18)),
    # cus_003: card declined, invoice still open
    ("pay_003", "cus_003", "inv_003", 2500, "usd", "failed", "card_declined", ago(days=3)),
    # cus_004: one larger charge because of overage
    ("pay_004", "cus_004", "inv_004", 6140, "usd", "succeeded", None, ago(days=22)),
    # cus_005: healthy
    ("pay_005", "cus_005", "inv_005", 2500, "usd", "succeeded", None, ago(days=10)),
    # cus_006: charged twice, and the duplicate has already been refunded
    ("pay_006a", "cus_006", "inv_006", 2500, "usd", "succeeded", None, ago(days=25, seconds=30)),
    ("pay_006b", "cus_006", "inv_006", 2500, "usd", "refunded", None, ago(days=25)),
]

ERROR_LOGS = [
    # cus_001: stale tokens after the subscription failed to activate
    ("cus_001", ago(hours=5), "auth", "jwt_expired", "JWT expired: token exp claim is in the past"),
    ("cus_001", ago(hours=4, minutes=40), "auth", "jwt_expired", "JWT expired: token exp claim is in the past"),
    ("cus_001", ago(hours=4), "auth", "invalid_jwt", "invalid JWT: signature verification failed"),
    ("cus_001", ago(hours=1), "auth", "invalid_jwt", "invalid JWT: signature verification failed"),
    # cus_003: project restricted while payment is past due
    ("cus_003", ago(days=2), "api", "project_paused", "Project is paused due to an unpaid invoice"),
    ("cus_003", ago(days=1), "api", "project_paused", "Project is paused due to an unpaid invoice"),
    # cus_005: auth misconfiguration, with no billing problem
    ("cus_005", ago(hours=6), "auth", "redirect_url_mismatch", "redirect_to URL is not in the allowed redirect list"),
    ("cus_005", ago(hours=5), "auth", "redirect_url_mismatch", "redirect_to URL is not in the allowed redirect list"),
    ("cus_005", ago(hours=2), "auth", "invalid_jwt", "invalid JWT: unable to parse or verify signature"),
]

KNOWN_ISSUES = [
    ("ki_001", "Subscription stays inactive after successful payment",
     "Payment succeeds but the subscription status is not updated to active",
     "investigating", "Support can re-sync the subscription manually"),
    ("ki_002", "Duplicate charge on checkout retry",
     "Customers who retry checkout during a slow response are charged twice",
     "investigating", "The duplicate charge is refunded by billing support"),
    ("ki_003", "JWT errors after key rotation",
     "Clients using tokens signed with a rotated key receive invalid JWT errors",
     "resolved", "Sign in again to get a token signed with the new key"),
]


def seed():
    init_db()

    with get_connection() as connection:
        connection.executemany("INSERT INTO customers VALUES (?,?,?,?)", CUSTOMERS)
        connection.executemany("INSERT INTO subscriptions VALUES (?,?,?,?,?,?)", SUBSCRIPTIONS)
        connection.executemany("INSERT INTO invoices VALUES (?,?,?,?,?,?,?,?)", INVOICES)
        connection.executemany("INSERT INTO payments VALUES (?,?,?,?,?,?,?,?)", PAYMENTS)
        connection.executemany(
            "INSERT INTO error_logs (customer_id, occurred_at, service, code, message) VALUES (?,?,?,?,?)",
            ERROR_LOGS,
        )
        connection.executemany("INSERT INTO known_issues VALUES (?,?,?,?,?)", KNOWN_ISSUES)


if __name__ == "__main__":
    seed()
    print(f"seeded {DB_PATH}")
