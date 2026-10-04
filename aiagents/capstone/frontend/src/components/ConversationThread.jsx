import { Link } from "react-router-dom";

import { StatusBadge } from "./Badges.jsx";
import { timeAgo } from "../lib/receipts.js";

// The whole conversation a ticket belongs to, for the team. Each turn links to
// its own ticket page, and the one being viewed is marked.
export default function ConversationThread({ turns, currentId, now }) {
  return (
    <ol className="flex flex-col gap-2">
      {turns.map((turn) => {
        const current = turn.ticket_id === currentId;

        return (
          <li key={turn.ticket_id}>
            <Link
              to={`/team/${turn.ticket_id}`}
              aria-current={current ? "page" : undefined}
              className={`flex flex-col gap-1.5 rounded-xl border px-3 py-2.5 transition-colors ${
                current ? "border-signal-dim bg-ink-800" : "border-ink-700 bg-ink-900 hover:border-ink-500"
              }`}
            >
              <span className="flex items-center justify-between gap-2">
                <span className="font-mono text-[11px] text-ink-500">{timeAgo(turn.created_at, now)}</span>
                <StatusBadge ticket={turn} />
              </span>
              <span className="line-clamp-2 text-sm text-ink-100">{turn.message}</span>
              {turn.reply && <span className="line-clamp-2 text-xs leading-snug text-ink-300">{turn.reply}</span>}
              {turn.human_reply && (
                <span className="line-clamp-2 text-xs leading-snug text-signal">Team: {turn.human_reply}</span>
              )}
            </Link>
          </li>
        );
      })}
    </ol>
  );
}
