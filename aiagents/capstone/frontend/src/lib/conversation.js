// Pure helpers for conversation history. No React in here, so they can be tested alone.

// A stored turn is one customer message and the reply they were shown. A turn
// may also carry a human's reply, once a person has answered an escalation.
export function turnsToMessages(turns) {
  return turns.flatMap((turn) => {
    const messages = [
      { id: `${turn.ticket_id}-q`, role: "user", text: turn.message },
      {
        id: `${turn.ticket_id}-a`,
        role: "assistant",
        restored: { reply: turn.reply, status: turn.status, review: turn.review, ticketId: turn.ticket_id },
      },
    ];

    if (turn.human_reply) {
      messages.push({ id: `${turn.ticket_id}-h`, role: "human", text: turn.human_reply, ticketId: turn.ticket_id });
    }

    return messages;
  });
}

function ticketIdOf(message) {
  if (message.role !== "assistant") return null;
  return message.restored?.ticketId ?? message.run?.ticketId ?? null;
}

// Add a human's reply right after the assistant message it answers. Replies that
// are already shown are left alone, and nothing else in the chat is touched, so a
// live run in progress is never disturbed.
export function mergeHumanReplies(messages, turns) {
  const shown = new Set(messages.filter((m) => m.role === "human").map((m) => m.ticketId));
  const missing = turns.filter((turn) => turn.human_reply && !shown.has(turn.ticket_id));
  if (missing.length === 0) return messages;

  const result = [];
  for (const message of messages) {
    result.push(message);

    const turn = missing.find((t) => t.ticket_id === ticketIdOf(message));
    if (turn) {
      result.push({ id: `${turn.ticket_id}-h`, role: "human", text: turn.human_reply, ticketId: turn.ticket_id });
    }
  }
  return result;
}

// True while an escalated reply is still waiting for a person to answer it.
export function awaitingHuman(messages) {
  return messages.some((message, index) => {
    const open = message.restored?.review === "open" || message.run?.status === "escalated" || message.run?.needsHuman;
    return Boolean(open) && messages[index + 1]?.role !== "human";
  });
}

// ---- remembering the conversation across a page refresh ----

const key = (customerId) => `supportdesk.conversation.${customerId}`;

export function loadConversationId(customerId, storage = globalThis.localStorage) {
  try {
    return storage?.getItem(key(customerId)) || null;
  } catch {
    return null;
  }
}

export function saveConversationId(customerId, conversationId, storage = globalThis.localStorage) {
  try {
    if (conversationId) storage?.setItem(key(customerId), conversationId);
    else storage?.removeItem(key(customerId));
  } catch {
    // storage can be blocked or full. The chat still works, it just will not survive a refresh.
  }
}
