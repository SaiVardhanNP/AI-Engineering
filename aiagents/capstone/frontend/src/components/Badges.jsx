const STATUS = {
  replied: { label: "Replied", className: "border-ink-700 text-ink-300" },
  open: { label: "Needs review", className: "border-alert/60 text-alert" },
  resolved: { label: "Resolved", className: "border-signal-dim text-signal" },
};

// A ticket can be answered by the assistant and still need a person (a refund, say),
// so what matters is the review state and not whether the assistant replied.
export function ticketState(ticket) {
  if (ticket.review === "open") return "open";
  if (ticket.review === "resolved") return "resolved";
  return "replied";
}

export function StatusBadge({ ticket }) {
  const state = STATUS[ticketState(ticket)];

  return (
    <span className={`whitespace-nowrap rounded-md border px-2 py-0.5 text-xs ${state.className}`}>
      {state.label}
    </span>
  );
}

export function CategoryChips({ categories }) {
  return (
    <span className="flex flex-wrap gap-1.5">
      {categories.map((category) => (
        <span
          key={category}
          className="rounded-md border border-ink-700 px-1.5 py-0.5 font-mono text-[10px] text-ink-300"
        >
          {category}
        </span>
      ))}
    </span>
  );
}
