// A scripted replay of what the real backend streams for the headline ticket
// (billing + technical in parallel, then the account check, then evaluation).
// It exists so the UI can be designed and tested with no backend and no LLM quota.

const wait = (ms, signal) =>
  new Promise((resolve, reject) => {
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener("abort", () => {
      clearTimeout(timer);
      reject(new DOMException("Aborted", "AbortError"));
    });
  });

const REPLY =
  "We can see you were charged twice: two payments of $25.00 on invoice inv_001, and no refund has been issued yet. " +
  "Your subscription shows as inactive even though the invoice is paid. " +
  "Your logs show expired and invalid token errors. Syncing your computer's clock and signing in again usually fixes these. " +
  "A team member will review the duplicate charge and the inactive subscription.";

export async function* mockStream({ signal }) {
  const started = performance.now();
  const at = () => Math.round((performance.now() - started) / 100) / 10;
  const send = async (delay, event) => {
    await wait(delay, signal);
    return { ...event, t: at() };
  };

  try {
    yield await send(0, { type: "stage", stage: "started", label: "Got your message" });
    yield await send(150, { type: "stage", stage: "classifying", label: "Reading your message" });
    yield await send(1200, {
      type: "stage",
      stage: "classified",
      label: "Understood: billing, account, technical",
      categories: ["billing", "account", "technical"],
    });
    yield await send(100, {
      type: "stage",
      stage: "investigating",
      label: "Investigating",
      domains: ["billing", "account", "technical"],
    });

    // billing and technical start together, which is the case the UI must keep readable
    yield await send(500, { type: "tool_start", agent: "billing", tool: "get_payment_details", label: "Checking your payments" });
    yield await send(60, { type: "tool_start", agent: "technical", tool: "get_error_logs", label: "Reading your recent error logs" });
    yield await send(500, { type: "tool_end", agent: "billing", tool: "get_payment_details", label: "Checking your payments", ok: true });
    yield await send(100, { type: "tool_start", agent: "billing", tool: "get_invoice", label: "Looking up your invoice" });
    yield await send(400, { type: "tool_end", agent: "technical", tool: "get_error_logs", label: "Reading your recent error logs", ok: true });
    yield await send(80, { type: "tool_start", agent: "technical", tool: "search_known_issues", label: "Searching known issues" });
    yield await send(300, { type: "tool_end", agent: "billing", tool: "get_invoice", label: "Looking up your invoice", ok: true });
    yield await send(60, { type: "tool_end", agent: "technical", tool: "search_known_issues", label: "Searching known issues", ok: true });
    yield await send(100, { type: "tool_start", agent: "technical", tool: "search_support_docs", label: "Searching the documentation" });
    yield await send(1600, { type: "tool_end", agent: "technical", tool: "search_support_docs", label: "Searching the documentation", ok: true });
    yield await send(300, { type: "tool_start", agent: "account", tool: "get_subscription_status", label: "Checking your subscription status" });
    yield await send(400, { type: "tool_end", agent: "account", tool: "get_subscription_status", label: "Checking your subscription status", ok: true });
    yield await send(1500, { type: "stage", stage: "checking", label: "Checking the reply against what we found", attempt: 1 });
    yield await send(1800, {
      type: "done",
      status: "reply",
      reply: REPLY,
      ticket_id: null,
      categories: ["billing", "account", "technical"],
      timings: {},
    });
  } catch (error) {
    if (error.name !== "AbortError") throw error;
  }
}
