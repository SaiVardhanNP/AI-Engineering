import { useState } from "react";
import { Link } from "react-router-dom";

import AppHeader from "../components/AppHeader.jsx";
import { CategoryChips, StatusBadge, ticketState } from "../components/Badges.jsx";
import { useFetch } from "../hooks/useFetch.js";
import { listTickets } from "../lib/api.js";
import { timeAgo } from "../lib/receipts.js";

const TABS = [
  { id: "open", label: "Needs review" },
  { id: "all", label: "All tickets" },
];

export function QueueList({ tickets, tab, now }) {
  const visible = tab === "open" ? tickets.filter((t) => ticketState(t) === "open") : tickets;

  if (visible.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-ink-700 p-8 text-center">
        <p className="text-sm text-ink-100">
          {tab === "open" ? "Nothing is waiting for a human." : "No tickets yet."}
        </p>
        <p className="mt-1 text-sm text-ink-300">
          Tickets appear here as soon as a customer sends one from the{" "}
          <Link to="/desk" className="text-signal underline underline-offset-4">
            customer view
          </Link>
          .
        </p>
      </div>
    );
  }

  return (
    <ul className="flex flex-col gap-3">
      {visible.map((ticket) => (
        <li key={ticket.id}>
          <Link
            to={`/team/${ticket.id}`}
            className="flex flex-col gap-2 rounded-xl border border-ink-700 bg-ink-900 p-4 transition-colors hover:border-ink-500"
          >
            <span className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-sm font-medium text-ink-100">{ticket.customer_name}</span>
              <span className="flex items-center gap-3">
                <span className="font-mono text-xs text-ink-500">{timeAgo(ticket.created_at, now)}</span>
                <StatusBadge ticket={ticket} />
              </span>
            </span>
            <span className="line-clamp-2 text-sm leading-relaxed text-ink-300">{ticket.message}</span>
            <span className="flex flex-wrap items-center gap-3">
              <CategoryChips categories={ticket.categories} />
              {ticket.message_count > 1 && (
                <span className="font-mono text-[11px] text-ink-500">{ticket.message_count} messages in this conversation</span>
              )}
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

function ListSkeleton() {
  return (
    <div className="flex flex-col gap-3" aria-label="Loading tickets">
      {[0, 1, 2].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl border border-ink-700 bg-ink-900" />
      ))}
    </div>
  );
}

export function LoadError({ error, onRetry }) {
  return (
    <div role="alert" className="flex flex-col items-start gap-3 rounded-xl border border-alert/50 p-4">
      <p className="text-sm text-ink-100">{error.message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="rounded-xl border border-ink-700 px-3 py-2 text-sm text-ink-100 transition hover:border-ink-500 active:scale-[0.98]"
      >
        Try again
      </button>
    </div>
  );
}

export default function Queue() {
  const [tab, setTab] = useState("open");
  const { data, error, loading, reload } = useFetch(listTickets);

  return (
    <div className="min-h-dvh">
      <AppHeader />

      <main className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-medium tracking-tight text-ink-100">Tickets</h1>
          <p className="text-sm text-ink-300">
            Everything the assistant handled, and the tickets it passed to a person.
          </p>
        </div>

        <div role="tablist" aria-label="Filter tickets" className="flex gap-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={tab === t.id}
              onClick={() => setTab(t.id)}
              className={`rounded-xl px-3 py-1.5 text-sm transition-colors ${
                tab === t.id ? "bg-ink-800 text-ink-100" : "text-ink-300 hover:text-ink-100"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {loading && !data && <ListSkeleton />}
        {error && <LoadError error={error} onRetry={reload} />}
        {data && <QueueList tickets={data} tab={tab} now={Date.now()} />}
      </main>
    </div>
  );
}
