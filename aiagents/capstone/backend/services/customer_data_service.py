from database import get_connection


class CustomerDataService:
    """Read-only lookups over the support database.

    Every method returns plain dicts. Expected problems (unknown customer,
    nothing found) come back as {"error": ...} instead of raising, so an agent
    can read the result and decide what to do next.
    """

    # ---------- billing ----------

    def get_payment_details(self, customer_id, limit=10):
        with get_connection() as connection:
            if not self._customer_exists(connection, customer_id):
                return self._unknown_customer(customer_id)

            payments = self._rows(
                connection,
                """SELECT id, invoice_id, amount_cents, currency, status,
                          failure_code, created_at
                   FROM payments WHERE customer_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (customer_id, limit),
            )

        # an invoice with more than one succeeded charge was charged twice
        succeeded_per_invoice = {}
        for payment in payments:
            if payment["status"] == "succeeded" and payment["invoice_id"]:
                succeeded_per_invoice.setdefault(payment["invoice_id"], []).append(payment["id"])

        return {
            "customer_id": customer_id,
            "payments": payments,
            "invoices_charged_more_than_once": {
                invoice_id: payment_ids
                for invoice_id, payment_ids in succeeded_per_invoice.items()
                if len(payment_ids) > 1
            },
        }

    def get_invoice(self, customer_id, invoice_id=None):
        with get_connection() as connection:
            if not self._customer_exists(connection, customer_id):
                return self._unknown_customer(customer_id)

            if invoice_id:
                invoices = self._rows(
                    connection,
                    "SELECT * FROM invoices WHERE customer_id = ? AND id = ?",
                    (customer_id, invoice_id),
                )
            else:
                invoices = self._rows(
                    connection,
                    "SELECT * FROM invoices WHERE customer_id = ? ORDER BY created_at DESC LIMIT 1",
                    (customer_id,),
                )

        if not invoices:
            return {"error": "invoice_not_found", "customer_id": customer_id, "invoice_id": invoice_id}

        return {"customer_id": customer_id, "invoice": invoices[0]}

    def get_subscription_billing(self, customer_id):
        with get_connection() as connection:
            if not self._customer_exists(connection, customer_id):
                return self._unknown_customer(customer_id)

            subscription = self._rows(
                connection,
                "SELECT id, plan, status FROM subscriptions WHERE customer_id = ?",
                (customer_id,),
            )
            open_invoices = self._rows(
                connection,
                "SELECT id, amount_cents, created_at FROM invoices WHERE customer_id = ? AND status = 'open'",
                (customer_id,),
            )

        return {
            "customer_id": customer_id,
            "subscription": subscription[0] if subscription else None,
            "open_invoices": open_invoices,
            "amount_due_cents": sum(invoice["amount_cents"] for invoice in open_invoices),
        }

    # ---------- account ----------

    def get_account_status(self, customer_id):
        with get_connection() as connection:
            customers = self._rows(
                connection,
                "SELECT id, name, email, created_at FROM customers WHERE id = ?",
                (customer_id,),
            )

        if not customers:
            return self._unknown_customer(customer_id)

        return {"customer": customers[0]}

    def get_subscription_status(self, customer_id):
        with get_connection() as connection:
            if not self._customer_exists(connection, customer_id):
                return self._unknown_customer(customer_id)

            subscriptions = self._rows(
                connection,
                """SELECT id, plan, status, started_at, current_period_end
                   FROM subscriptions WHERE customer_id = ?""",
                (customer_id,),
            )

        if not subscriptions:
            return {"error": "no_subscription", "customer_id": customer_id}

        return {"customer_id": customer_id, "subscription": subscriptions[0]}

    # ---------- technical ----------

    def get_error_logs(self, customer_id, limit=10):
        with get_connection() as connection:
            if not self._customer_exists(connection, customer_id):
                return self._unknown_customer(customer_id)

            logs = self._rows(
                connection,
                """SELECT occurred_at, service, code, message
                   FROM error_logs WHERE customer_id = ?
                   ORDER BY occurred_at DESC LIMIT ?""",
                (customer_id, limit),
            )

        counts = {}
        for log in logs:
            counts[log["code"]] = counts.get(log["code"], 0) + 1

        return {"customer_id": customer_id, "errors": logs, "count_by_code": counts}

    def search_known_issues(self, query, limit=5):
        # naive keyword match: an issue matches if any query word appears in it
        words = [word.lower() for word in query.split() if len(word) > 2]

        with get_connection() as connection:
            issues = self._rows(
                connection,
                "SELECT id, title, symptom, status, workaround FROM known_issues",
                (),
            )

        def matches(issue):
            text = f"{issue['title']} {issue['symptom']}".lower()
            return sum(word in text for word in words)

        ranked = sorted(
            (issue for issue in issues if matches(issue) > 0),
            key=matches,
            reverse=True,
        )

        return {"query": query, "issues": ranked[:limit]}

    # ---------- helpers ----------

    def _customer_exists(self, connection, customer_id):
        row = connection.execute(
            "SELECT 1 FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchone()
        return row is not None

    def _rows(self, connection, sql, params):
        return [dict(row) for row in connection.execute(sql, params).fetchall()]

    def _unknown_customer(self, customer_id):
        return {"error": "customer_not_found", "customer_id": customer_id}
