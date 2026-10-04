// A recorded ticket from a real run of the backend (customer data is fictional).
// The landing page uses it so its demos are real components with real data.
export const SAMPLE_TICKET = {
  "id": "tkt_b1fb2f82",
  "customer_name": "Alice Rao",
  "message": "I was charged twice for my Pro subscription. My subscription still shows inactive, and my dashboard is returning an authentication error.",
  "categories": [
    "billing",
    "account",
    "technical"
  ],
  "reply": "Hello,\n\nWe have confirmed that you were charged twice for your Pro subscription on invoice `inv_001` with two successful payments (`pay_001a` and `pay_001b`), and that your subscription status currently shows as inactive despite the paid invoice. No refund has been issued yet. A team member will handle your account.\n\nRegarding the authentication error on your dashboard, our logs show `invalid_jwt` and `jwt_expired` errors. When the dashboard issues JWT expired errors, it usually means your computer's time is not in sync with the actual time. You can go to https://time.is/ to compare your computer's clock with your local time and sync it if it is inaccurate. For the invalid JWT errors related to key rotation, you can sign in again to get a token signed with the new key.",
  "claims": [
    {
      "statement": "We have confirmed that you were charged twice for your Pro subscription on invoice inv_001 with two successful payments (pay_001a and pay_001b)",
      "supporting_quote": "Confirmed: The customer was charged twice for the same invoice (`inv_001`) with two successful $25.00 payments (`pay_001a` and `pay_001b`)."
    },
    {
      "statement": "your subscription status currently shows as inactive despite the paid invoice",
      "supporting_quote": "Confirmed: The subscription status currently shows as `inactive` despite the invoice being paid."
    },
    {
      "statement": "No refund has been issued yet.",
      "supporting_quote": "No refund has been issued yet for either duplicate charge."
    },
    {
      "statement": "our logs show invalid_jwt and jwt_expired errors",
      "supporting_quote": "invalid_jwt (\"invalid JWT: signature verification failed\", 2 occurrences)"
    },
    {
      "statement": "When the dashboard issues JWT expired errors, it usually means your computer's time is not in sync with the actual time.",
      "supporting_quote": "When the Dashboard issues JWT expired errors, it usually means your computer's time is not in sync with the actual time."
    },
    {
      "statement": "You can go to https://time.is/ to compare your computer's clock with your local time and sync it if it is inaccurate.",
      "supporting_quote": "Go to https://time.is/ to compare your computer's clock with your local time. If your computer's time is inaccurate, sync it to resolve the issue."
    },
    {
      "statement": "For the invalid JWT errors related to key rotation, you can sign in again to get a token signed with the new key.",
      "supporting_quote": "Workaround: Sign in again to get a token signed with the new key."
    }
  ],
  "findings": "## BILLING FINDINGS\nInternal billing findings:\n\n- **Payments**: \n  - Payment ID `pay_001a` for invoice `inv_001` (Amount: $25.00 USD / 2500 cents, Status: `succeeded`, Date: `2026-10-03T07:55:34+00:00`)\n  - Payment ID `pay_001b` for invoice `inv_001` (Amount: $25.00 USD / 2500 cents, Status: `succeeded`, Date: `2026-10-03T07:56:14+00:00`)\n  - Invoice `inv_001` was charged twice via payments `pay_001a` and `pay_001b`.\n\n- **Invoices**: \n  - Most recent invoice ID: `inv_001`\n  - Amount: $25.00 USD (2500 cents)\n  - Status: `paid`\n  - Created at: `2026-10-03T07:56:14+00:00`\n  - Period: `2026-10-03` to `2026-11-02`\n  - Subscription ID: `sub_001`\n\n- **Subscription Billing**:\n  - Plan: Pro (`sub_001`)\n  - Status: `inactive`\n  - Open invoices: None (0)\n  - Amount currently due: $0.00 (0 cents)\n\n- **Customer Complaint Confirmation**:\n  - Confirmed: The customer was charged twice for the same invoice (`inv_001`) with two successful $25.00 payments (`pay_001a` and `pay_001b`).\n  - Confirmed: The subscription status currently shows as `inactive` despite the invoice being paid.\n\n- **Refund Status**:\n  - No refund has been issued yet for either duplicate charge.\n\n## TECHNICAL FINDINGS\nInternal technical findings:\n\n- **Errors seen in the logs:**\n  - `invalid_jwt` (\"invalid JWT: signature verification failed\", 2 occurrences)\n  - `jwt_expired` (\"JWT expired: token exp claim is in the past\", 2 occurrences)\n\n- **Matching known issues:**\n  - *Known Issue 1 (ki_003):* \"JWT errors after key rotation\" (Status: resolved). Symptom: Clients using tokens signed with a rotated key receive invalid JWT errors. Workaround: Sign in again to get a token signed with the new key.\n  - *Known Issue 2 (ki_001):* \"Subscription stays inactive after successful payment\" (Status: investigating). Symptom: Payment succeeds but the subscription status is not updated to active. Workaround: Support can re-sync the subscription manually.\n\n- **What the docs say:**\n  - Regarding the `jwt_expired` error, the documentation (\"Jwt Expired Error In Supabase Dashboard F06K3X\") states: \"When the Dashboard issues JWT expired errors, it usually means your computer's time is not in sync with the actual time. Go to https://time.is/ to compare your computer's clock with your local time. If your computer's time is inaccurate, sync it to resolve the issue.\"\n  - Regarding the authentication/login/dashboard issues, the documentation search results for billing/double charges or specific payment processing docs were weak/unrelated. Therefore, the documentation does not cover the double charge or subscription payment failure aspects.\n\n- **What remains unexplained:**\n  - The double charge report by the customer is not explained by the logs, known issues, or documentation.\n  - The root cause of why the payment failed to update the subscription status to active (beyond matching the known issue symptom) remains unexplained in the logs.\n\n## ACCOUNT FINDINGS\nInternal account findings:\n- **Account details**: Name: Alice Rao, Email: alice@example.com, Created at: 2026-03-18T07:56:14+00:00.\n- **Subscription plan and status**: Plan: `pro` (Subscription ID: `sub_001`), Status: `inactive`, Started at: `2026-10-03T07:56:14+00:00`.\n- **Consistency with billing findings**: The billing findings show that invoice `inv_001` for the Pro subscription was successfully paid twice (payments `pay_001a` and `pay_001b` on 2026-10-03, totaling $50.00 / 5000 cents for a $25.00 invoice) and the invoice status is `paid`. A successful payment on the invoice should have made the subscription active. Therefore, the subscription state (`inactive`) is **inconsistent** with the billing findings, as the subscription is currently inactive despite the associated invoice being fully paid."
};
