import { mockStream } from "./mockStream.js";

export const API_URL = import.meta.env?.VITE_API_URL ?? "http://localhost:8000";
export const USE_MOCK = import.meta.env?.VITE_MOCK === "true";

/*
  Event shapes sent by POST /tickets/stream (every event also has `t`, seconds
  since the request started):

    { type: "stage",      stage, label, categories?, domains?, attempt? }
    { type: "tool_start", agent, tool, label }
    { type: "tool_end",   agent, tool, label, ok }
    { type: "done",       ticket_id, conversation_id, status: "reply" | "escalated",
                          reply, categories, timings }
    { type: "error",      message }
*/

// Parses a server-sent-event body. EventSource cannot POST, so this reads the
// response with fetch() and splits it on blank lines itself.
export async function* readEvents(response) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop(); // the last piece may be incomplete

    for (const block of blocks) {
      const line = block.split("\n").find((l) => l.startsWith("data: "));
      if (line) yield JSON.parse(line.slice(6));
    }
  }
}

export async function* streamTicket({ customerId, message, conversationId, signal }) {
  if (USE_MOCK) {
    yield* mockStream({ customerId, message, signal });
    return;
  }

  let response;
  try {
    response = await fetch(`${API_URL}/tickets/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer_id: customerId, message, conversation_id: conversationId ?? null }),
      signal,
    });
  } catch (error) {
    if (error.name === "AbortError") return;
    yield { type: "error", message: "Cannot reach the support service. Is the backend running?" };
    return;
  }

  if (!response.ok) {
    yield { type: "error", message: await describeFailure(response) };
    return;
  }

  try {
    yield* readEvents(response);
  } catch (error) {
    if (error.name !== "AbortError") {
      yield { type: "error", message: "The connection dropped before the reply finished." };
    }
  }
}

async function describeFailure(response) {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
  } catch {
    // fall through to the generic message
  }
  return `The support service returned an error (${response.status}).`;
}
