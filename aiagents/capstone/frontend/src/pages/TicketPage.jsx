import { ArrowLeft, CaretDown } from "@phosphor-icons/react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import AppHeader from "../components/AppHeader.jsx";
import { CategoryChips, StatusBadge, ticketState } from "../components/Badges.jsx";
import ConversationThread from "../components/ConversationThread.jsx";
import CrewMap from "../components/CrewMap.jsx";
import EvidenceReply from "../components/EvidenceReply.jsx";
import ResolveForm from "../components/ResolveForm.jsx";
import { useFetch } from "../hooks/useFetch.js";
import { getTeamConversation, getTicket } from "../lib/api.js";
import { parseFindings, timeAgo } from "../lib/receipts.js";
import { AGENT_KEYS } from "../lib/runReducer.js";
import { LoadError } from "./Queue.jsx";

// The final state of the crew for a stored ticket.
function crewStates(ticket) {
  const agents = Object.fromEntries(AGENT_KEYS.map((key) => [key, "idle"]));
  // only real specialist domains count, "clarify" and "other" never reach the specialists
  const domains = ticket.categories.filter((c) => ["billing", "account", "technical"].includes(c));

  agents.router = "done";
  if (domains.length === 0) return agents;

  for (const domain of domains) agents[domain] = "done";
  agents.responder = "done";
  agents.evaluator = ticket.status === "escalated" ? "failed" : "done";
  return agents;
}

function Section({ title, children }) {
  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-sm font-medium text-ink-100">{title}</h2>
      {children}
    </section>
  );
}

function Disclosure({ title, meta, children }) {
  return (
    <details className="group rounded-xl border border-ink-700 bg-ink-900">
      <summary className="flex cursor-pointer list-none items-center gap-3 px-4 py-3">
        <span className="flex-1 text-sm capitalize text-ink-100">{title}</span>
        {meta && <span className="font-mono text-xs text-ink-500">{meta}</span>}
        <CaretDown size={14} aria-hidden className="text-ink-300 transition-transform group-open:rotate-180" />
      </summary>
      <div className="border-t border-ink-700 px-4 py-3">{children}</div>
    </details>
  );
}

export function TicketView({ ticket, now, onResolved, thread = null }) {
  const state = ticketState(ticket);
  const escalated = ticket.status === "escalated";
  const findings = parseFindings(ticket.findings);
  const replyText = escalated ? ticket.draft : ticket.reply;
  const clarified = ticket.categories.includes("clarify");

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-medium tracking-tight text-ink-100">{ticket.customer_name}</h1>
          <StatusBadge ticket={ticket} />
          <span className="font-mono text-xs text-ink-500">{timeAgo(ticket.created_at, now)}</span>
        </div>
        <CategoryChips categories={ticket.categories} />
        <blockquote className="max-w-[70ch] rounded-xl border border-ink-700 bg-ink-900 px-4 py-3 text-sm leading-relaxed text-ink-100">
          {ticket.message}
        </blockquote>
      </div>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="flex min-w-0 flex-col gap-8">
          {escalated && (
            <p className="rounded-xl border border-alert/50 px-4 py-3 text-sm leading-relaxed text-ink-100">
              The assistant did not send a reply. {ticket.escalation_reason}. The customer was told a team member
              will follow up.
            </p>
          )}

          {clarified && (
            <Section title="What the customer was told">
              <p className="rounded-xl border border-ink-700 bg-ink-900 px-4 py-3 text-xs leading-relaxed text-ink-300">
                This was a greeting or a message without enough detail, so the assistant asked for more. No
                specialists ran and nothing needed checking.
              </p>
              <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-ink-100">{ticket.reply}</p>
            </Section>
          )}

          {!escalated && state === "open" && (
            <p className="rounded-xl border border-alert/50 px-4 py-3 text-sm leading-relaxed text-ink-100">
              The assistant answered, and told the customer a person will follow up: {ticket.escalation_reason}.
            </p>
          )}

          {replyText && !clarified && (
            <Section title={escalated ? "The assistant's last draft (not sent)" : "What the customer was told"}>
              <EvidenceReply text={replyText} claims={ticket.claims ?? []} findings={ticket.findings ?? ""} />
            </Section>
          )}

          {state === "resolved" && (
            <Section title="Reply from the team">
              <p className="whitespace-pre-wrap rounded-xl border border-signal-dim px-4 py-3 text-[15px] leading-relaxed text-ink-100">
                {ticket.human_reply}
              </p>
            </Section>
          )}

          {state === "open" && (
            <Section title="Reply as a human">
              <ResolveForm ticket={ticket} onResolved={onResolved} />
            </Section>
          )}

          {findings.length > 0 && (
            <Section title="What each specialist found">
              <div className="flex flex-col gap-2">
                {findings.map((section) => (
                  <Disclosure key={section.name} title={section.name}>
                    <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-ink-300">
                      {section.text}
                    </pre>
                  </Disclosure>
                ))}
              </div>
            </Section>
          )}

          {(ticket.attempts?.length ?? 0) > 0 && (
            <Section title="Drafts and checks">
              <div className="flex flex-col gap-2">
                {ticket.attempts.map((attempt, index) => (
                  <Disclosure
                    key={index}
                    title={`Draft ${index + 1}`}
                    meta={attempt.passed ? "passed" : `${attempt.problems.length} problem(s)`}
                  >
                    {attempt.problems.length > 0 && (
                      <ul className="mb-3 list-disc pl-5 text-sm leading-relaxed text-alert">
                        {attempt.problems.map((problem, i) => (
                          <li key={i}>{problem}</li>
                        ))}
                      </ul>
                    )}
                    <p className="whitespace-pre-wrap text-sm leading-relaxed text-ink-300">{attempt.draft}</p>
                  </Disclosure>
                ))}
              </div>
            </Section>
          )}
        </div>

        <aside className="flex flex-col gap-8 lg:sticky lg:top-20 lg:self-start">
          {thread && thread.turns.length > 1 && (
            <Section title={`This conversation (${thread.turns.length} messages)`}>
              <ConversationThread turns={thread.turns} currentId={ticket.id} now={now} />
            </Section>
          )}

          <Section title="Crew">
            <div className="rounded-xl border border-ink-700 bg-ink-900 p-4">
              <CrewMap agents={crewStates(ticket)} />
            </div>
          </Section>

          {Object.keys(ticket.timings ?? {}).length > 0 && (
            <Section title="Time per step">
              <dl className="flex flex-col gap-1.5 text-sm">
                {Object.entries(ticket.timings).map(([step, seconds]) => (
                  <div key={step} className="flex justify-between gap-4">
                    <dt className="text-ink-300">{step.replaceAll("_", " ")}</dt>
                    <dd className="font-mono text-ink-100">{seconds.toFixed(1)}s</dd>
                  </div>
                ))}
              </dl>
            </Section>
          )}
        </aside>
      </div>
    </div>
  );
}

export default function TicketPage() {
  const { ticketId } = useParams();
  const { data, error, loading, reload } = useFetch(() => getTicket(ticketId), [ticketId]);
  const [resolved, setResolved] = useState(null);

  const ticket = resolved?.id === ticketId ? resolved : data;

  // the rest of the conversation this ticket belongs to, if it has one
  const conversationId = ticket?.conversation_id ?? null;
  const { data: thread } = useFetch(
    () => (conversationId ? getTeamConversation(conversationId) : Promise.resolve(null)),
    [conversationId],
  );

  return (
    <div className="min-h-dvh">
      <AppHeader />

      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8">
        <Link to="/team" className="flex w-fit items-center gap-2 text-sm text-ink-300 transition-colors hover:text-ink-100">
          <ArrowLeft size={14} aria-hidden />
          All tickets
        </Link>

        {loading && !ticket && <div className="h-64 animate-pulse rounded-xl border border-ink-700 bg-ink-900" aria-label="Loading ticket" />}
        {error && <LoadError error={error} onRetry={reload} />}
        {ticket && <TicketView ticket={ticket} now={Date.now()} onResolved={setResolved} thread={thread} />}
      </main>
    </div>
  );
}
