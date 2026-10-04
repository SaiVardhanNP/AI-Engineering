import { useMemo, useState } from "react";

import { matchClaims } from "../lib/receipts.js";

const QUOTE_LABEL = {
  exact: { text: "Found word for word in the findings", className: "text-signal" },
  approximate: { text: "Approximate match in the findings", className: "text-ink-300" },
  missing: { text: "No supporting evidence", className: "text-alert" },
};

function Receipt({ claim }) {
  const label = QUOTE_LABEL[claim.quote_status];

  return (
    <li className="flex flex-col gap-2 rounded-xl border border-ink-700 bg-ink-900 p-3">
      <p className="text-sm leading-snug text-ink-100">{claim.statement}</p>
      {claim.supporting_quote && (
        <blockquote className="border-l-2 border-ink-700 pl-3 font-mono text-xs leading-relaxed text-ink-300">
          {claim.supporting_quote}
        </blockquote>
      )}
      <p className={`text-xs ${label.className}`}>{label.text}</p>
    </li>
  );
}

// The reply, with each sentence linked to the claims checked against it. Hover,
// focus or tap a sentence to see its evidence.
export default function EvidenceReply({ text, claims, findings }) {
  const { sentences, unattached } = useMemo(() => matchClaims(text, claims, findings), [text, claims, findings]);
  const [active, setActive] = useState(null);

  const exact = claims.filter((c) => matchClaims("x", [c], findings).unattached[0].quote_status === "exact").length;
  const shown = active == null ? [] : sentences[active].receipts;

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
      <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-ink-100">
        {sentences.map((sentence, index) => {
          const linked = sentence.receipts.length > 0;

          return (
            <span key={index}>
              {linked ? (
                <button
                  type="button"
                  onMouseEnter={() => setActive(index)}
                  onFocus={() => setActive(index)}
                  onClick={() => setActive(index)}
                  aria-pressed={active === index}
                  className={`text-left underline decoration-signal-dim decoration-dotted underline-offset-4 transition-colors hover:bg-ink-800 ${
                    active === index ? "bg-ink-800" : ""
                  }`}
                >
                  {sentence.text}
                </button>
              ) : (
                <span>{sentence.text}</span>
              )}
              {sentence.after}
            </span>
          );
        })}
      </p>

      <div className="flex flex-col gap-3" aria-live="polite">
        <h3 className="text-sm font-medium text-ink-100">Evidence</h3>

        {active == null ? (
          <p className="text-xs leading-relaxed text-ink-300">
            {claims.length === 0
              ? "No claims were recorded for this reply."
              : `${claims.length} claims were checked and ${exact} of them were found word for word in the findings. Hover or tap an underlined sentence to see its evidence.`}
          </p>
        ) : (
          <ul className="flex flex-col gap-2">
            {shown.map((claim, i) => (
              <Receipt key={i} claim={claim} />
            ))}
          </ul>
        )}

        {unattached.length > 0 && (
          <details className="rounded-xl border border-ink-700 bg-ink-900 px-3 py-2">
            <summary className="cursor-pointer text-xs text-ink-300">
              {unattached.length} more claim{unattached.length === 1 ? "" : "s"} checked
            </summary>
            <ul className="mt-2 flex flex-col gap-2">
              {unattached.map((claim, i) => (
                <Receipt key={i} claim={claim} />
              ))}
            </ul>
          </details>
        )}
      </div>
    </div>
  );
}
