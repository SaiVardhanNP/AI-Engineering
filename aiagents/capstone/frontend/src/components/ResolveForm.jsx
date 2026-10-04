import { PaperPlaneRight } from "@phosphor-icons/react";
import { useState } from "react";

import { resolveTicket } from "../lib/api.js";

export default function ResolveForm({ ticket, onResolved }) {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  async function submit(event) {
    event.preventDefault();
    if (!text.trim() || sending) return;

    setSending(true);
    setError(null);
    try {
      onResolved(await resolveTicket(ticket.id, text.trim()));
    } catch (failure) {
      setError(failure.message);
      setSending(false);
    }
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-3 rounded-xl border border-ink-700 bg-ink-900 p-4">
      <label htmlFor="human-reply" className="text-sm font-medium text-ink-100">
        Your reply to the customer
      </label>
      <textarea
        id="human-reply"
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={5}
        maxLength={2000}
        className="resize-y rounded-xl border border-ink-700 bg-ink-950 p-3 text-sm leading-relaxed text-ink-100 outline-none focus:border-ink-500"
      />

      {error && (
        <p role="alert" className="text-sm text-alert">
          {error}
        </p>
      )}

      <div className="flex flex-wrap gap-2">
        <button
          type="submit"
          disabled={sending || !text.trim()}
          className="flex items-center gap-2 whitespace-nowrap rounded-xl bg-signal px-4 py-2 text-sm font-medium text-ink-950 transition active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
        >
          <PaperPlaneRight size={16} weight="bold" aria-hidden />
          Send reply
        </button>

        {ticket.draft && (
          <button
            type="button"
            onClick={() => setText(ticket.draft)}
            className="whitespace-nowrap rounded-xl border border-ink-700 px-4 py-2 text-sm text-ink-100 transition hover:border-ink-500 active:scale-[0.98]"
          >
            Start from AI draft
          </button>
        )}
      </div>
    </form>
  );
}
