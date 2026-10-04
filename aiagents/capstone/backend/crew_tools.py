import json

from crewai.tools import tool


def build_tools(customer_id, data_service, knowledge_service, kb_id="supabase"):
    """Create the agents' tools for ONE customer.

    customer_id is fixed here, from the session, and is not a parameter the LLM
    can set. An agent can only ever look up the customer who is asking.
    """

    @tool("Get Payment Details")
    def get_payment_details(reason: str = "") -> str:
        """Get this customer's recent payments, including failed and refunded
        ones, and which invoices were charged more than once.
        reason: optional short note on why you are looking this up.
        """
        return json.dumps(data_service.get_payment_details(customer_id))

    @tool("Get Invoice")
    def get_invoice(invoice_id: str = "") -> str:
        """Get one of this customer's invoices by invoice id. If no invoice id
        is given, returns the most recent invoice."""
        return json.dumps(data_service.get_invoice(customer_id, invoice_id or None))

    @tool("Get Subscription Billing")
    def get_subscription_billing(reason: str = "") -> str:
        """Get this customer's plan, subscription status, open invoices and the
        total amount currently due.
        reason: optional short note on why you are looking this up.
        """
        return json.dumps(data_service.get_subscription_billing(customer_id))

    @tool("Get Account Status")
    def get_account_status(reason: str = "") -> str:
        """Get this customer's account details: name, email and when the account
        was created.
        reason: optional short note on why you are looking this up.
        """
        return json.dumps(data_service.get_account_status(customer_id))

    @tool("Get Subscription Status")
    def get_subscription_status(reason: str = "") -> str:
        """Get this customer's subscription: plan, status (active, inactive,
        past_due or canceled), start date and current period end.
        reason: optional short note on why you are looking this up.
        """
        return json.dumps(data_service.get_subscription_status(customer_id))

    @tool("Get Error Logs")
    def get_error_logs(reason: str = "") -> str:
        """Get this customer's most recent error logs, newest first, with a
        count of each error code.
        reason: optional short note on why you are looking this up.
        """
        return json.dumps(data_service.get_error_logs(customer_id))

    @tool("Search Known Issues")
    def search_known_issues(query: str) -> str:
        """Search the list of known platform issues by keywords describing the
        symptom. Returns matching issues with their status and workaround."""
        return json.dumps(data_service.search_known_issues(query))

    @tool("Search Support Docs")
    def search_support_docs(query: str) -> str:
        """Search the product documentation and troubleshooting guides. Returns
        the best matching passages with their source and a relevance score.
        A low or negative score means the docs probably do not answer the
        question."""
        return json.dumps(knowledge_service.search(query, kb_id, top_k=3))

    return {
        "billing": [get_payment_details, get_invoice, get_subscription_billing, search_support_docs],
        "account": [get_account_status, get_subscription_status, search_support_docs],
        "technical": [get_error_logs, search_known_issues, search_support_docs],
    }
