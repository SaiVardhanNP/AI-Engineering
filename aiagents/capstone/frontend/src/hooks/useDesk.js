import { useCallback, useEffect, useReducer, useRef } from "react";

import { getConversation } from "../lib/api.js";
import {
  awaitingHuman,
  loadConversationId,
  mergeHumanReplies,
  saveConversationId,
  turnsToMessages,
} from "../lib/conversation.js";
import { CUSTOMERS } from "../lib/customers.js";
import { applyEvent, initialRun } from "../lib/runReducer.js";
import { USE_MOCK, streamTicket } from "../lib/stream.js";

// While a ticket is waiting for a person, check this often for their reply.
const POLL_MS = 8000;

export function reducer(state, action) {
  switch (action.type) {
    case "select":
      return { customerId: action.customerId, conversationId: null, messages: [], restoring: true };

    case "restored":
      return { ...state, conversationId: action.conversationId, messages: action.messages, restoring: false };

    case "restore_failed":
      return { ...state, conversationId: null, messages: [], restoring: false };

    case "new_conversation":
      return { ...state, conversationId: null, messages: [] };

    case "send":
      return {
        ...state,
        messages: [
          ...state.messages,
          { id: action.id, role: "user", text: action.text },
          { id: `${action.id}-reply`, role: "assistant", run: initialRun() },
        ],
      };

    case "event": {
      const messages = [...state.messages];
      const last = messages.length - 1;
      if (last < 0 || !messages[last].run) return state;

      messages[last] = { ...messages[last], run: applyEvent(messages[last].run, action.event) };

      let conversationId = state.conversationId;
      // the server decides which conversation a message belongs to, for example a
      // fresh one after a long silence, so always adopt what it reports
      if (action.event.type === "done" && action.event.conversation_id) {
        conversationId = action.event.conversation_id;
      }
      // the conversation no longer exists server side, so the next message starts a new one
      if (action.event.type === "error" && action.event.message === "Unknown conversation") {
        conversationId = null;
      }

      return { ...state, messages, conversationId };
    }

    case "human_replies":
      return { ...state, messages: mergeHumanReplies(state.messages, action.turns) };

    default:
      return state;
  }
}

export function useDesk() {
  const [state, dispatch] = useReducer(reducer, {
    customerId: CUSTOMERS[0].id,
    conversationId: null,
    messages: [],
    restoring: true,
  });

  const abortRef = useRef(null);
  const customerRef = useRef(state.customerId);
  const conversationRef = useRef(state.conversationId);
  customerRef.current = state.customerId;
  conversationRef.current = state.conversationId;

  useEffect(() => () => abortRef.current?.abort(), []);

  // Bring back this customer's conversation after a refresh or a customer switch.
  useEffect(() => {
    let cancelled = false;
    const id = USE_MOCK ? null : loadConversationId(state.customerId);

    if (!id) {
      dispatch({ type: "restored", conversationId: null, messages: [] });
      return undefined;
    }

    getConversation(id, state.customerId).then(
      (conversation) => {
        if (!cancelled) {
          dispatch({ type: "restored", conversationId: id, messages: turnsToMessages(conversation.turns) });
        }
      },
      () => {
        // gone or not ours: forget it and start clean
        saveConversationId(state.customerId, null);
        if (!cancelled) dispatch({ type: "restore_failed" });
      },
    );

    return () => {
      cancelled = true;
    };
  }, [state.customerId]);

  // Remember the conversation, but never while restoring: a customer switch must not
  // erase the id that is about to be read for the new customer.
  useEffect(() => {
    if (!state.restoring) saveConversationId(state.customerId, state.conversationId);
  }, [state.customerId, state.conversationId, state.restoring]);

  const lastAssistant = [...state.messages].reverse().find((m) => m.role === "assistant");
  const busy = lastAssistant?.run?.status === "running";
  const waiting = awaitingHuman(state.messages);

  // Pick up a person's reply to an escalated ticket without a refresh.
  useEffect(() => {
    if (USE_MOCK || !state.conversationId || !waiting || busy) return undefined;

    const timer = setInterval(() => {
      getConversation(state.conversationId, state.customerId).then(
        (conversation) => dispatch({ type: "human_replies", turns: conversation.turns }),
        () => {}, // try again on the next tick
      );
    }, POLL_MS);

    return () => clearInterval(timer);
  }, [state.conversationId, state.customerId, waiting, busy]);

  const send = useCallback(async (text) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    dispatch({ type: "send", id: crypto.randomUUID(), text });

    let finished = false;
    for await (const event of streamTicket({
      customerId: customerRef.current,
      message: text,
      conversationId: conversationRef.current,
      signal: controller.signal,
    })) {
      if (event.type === "done" || event.type === "error") finished = true;
      dispatch({ type: "event", event });
    }

    if (!finished && !controller.signal.aborted) {
      dispatch({ type: "event", event: { type: "error", message: "The connection closed before the reply finished." } });
    }
  }, []);

  const selectCustomer = useCallback((customerId) => {
    abortRef.current?.abort();
    dispatch({ type: "select", customerId });
  }, []);

  const newConversation = useCallback(() => {
    abortRef.current?.abort();
    dispatch({ type: "new_conversation" });
  }, []);

  const lastUser = [...state.messages].reverse().find((m) => m.role === "user");

  return {
    customerId: state.customerId,
    conversationId: state.conversationId,
    messages: state.messages,
    restoring: state.restoring,
    busy,
    waitingForHuman: waiting,
    lastUserText: lastUser?.text ?? null,
    send,
    selectCustomer,
    newConversation,
  };
}
