import { ArrowsClockwise, Headset } from "@phosphor-icons/react";
import { motion, useReducedMotion } from "motion/react";
import { Link } from "react-router-dom";

import ActivityTrace from "./ActivityTrace.jsx";

export function UserMessage({ text }) {
  return (
    <li className="flex justify-end">
      <p className="max-w-[85%] whitespace-pre-wrap rounded-xl border border-ink-700 bg-ink-800 px-4 py-3 text-sm leading-relaxed text-ink-100">
        {text}
      </p>
    </li>
  );
}

// Same shape as the reply will have, so the page does not jump when it arrives.
function ReplySkeleton() {
  return (
    <div className="flex flex-col gap-2 px-1 pt-1" aria-hidden>
      <div className="h-3 w-11/12 animate-pulse rounded-md bg-ink-800" />
      <div className="h-3 w-9/12 animate-pulse rounded-md bg-ink-800" />
      <div className="h-3 w-6/12 animate-pulse rounded-md bg-ink-800" />
    </div>
  );
}

export function AssistantMessage({ run, onRetry, canRetry }) {
  const reduce = useReducedMotion();

  return (
    <li className="flex flex-col gap-3">
      <ActivityTrace run={run} detailed={false} />

      {run.status === "running" && <ReplySkeleton />}

      {(run.status === "done" || run.status === "escalated") && (
        <motion.div
          initial={reduce ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col gap-3 px-1"
        >
          <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-ink-100">{run.reply}</p>

          {run.ticketId && (
            <Link
              to={`/team/${run.ticketId}`}
              className="w-fit text-xs text-ink-300 underline underline-offset-4 transition-colors hover:text-ink-100"
            >
              See how the crew handled this in the team view
            </Link>
          )}

          {run.status === "escalated" && (
            <p className="flex w-fit items-center gap-2 rounded-md border border-ink-700 px-2 py-1 text-xs text-ink-300">
              <Headset size={14} aria-hidden />
              Passed to a human
            </p>
          )}

          {run.status === "done" && run.needsHuman && (
            <p className="flex w-fit items-center gap-2 rounded-md border border-ink-700 px-2 py-1 text-xs text-ink-300">
              <Headset size={14} aria-hidden />
              A person will follow up
            </p>
          )}
        </motion.div>
      )}

      {run.status === "error" && (
        <div role="alert" className="flex flex-col items-start gap-3 rounded-xl border border-alert/50 px-4 py-3">
          <p className="text-sm text-ink-100">{run.error}</p>
          {canRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="flex items-center gap-2 rounded-xl border border-ink-700 px-3 py-2 text-sm text-ink-100 transition hover:border-ink-500 active:scale-[0.98]"
            >
              <ArrowsClockwise size={14} aria-hidden />
              Try again
            </button>
          )}
        </div>
      )}
    </li>
  );
}

// A reply that was loaded back from history. There was no live run, so there is
// no accordion, just the reply the customer was shown.
export function RestoredAssistantMessage({ restored }) {
  return (
    <li className="flex flex-col gap-3 px-1">
      <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-ink-100">{restored.reply}</p>

      <Link
        to={`/team/${restored.ticketId}`}
        className="w-fit text-xs text-ink-300 underline underline-offset-4 transition-colors hover:text-ink-100"
      >
        See how the crew handled this in the team view
      </Link>

      {restored.status === "escalated" && (
        <p className="flex w-fit items-center gap-2 rounded-md border border-ink-700 px-2 py-1 text-xs text-ink-300">
          <Headset size={14} aria-hidden />
          Passed to a human
        </p>
      )}

      {restored.status === "replied" && restored.review === "open" && (
        <p className="flex w-fit items-center gap-2 rounded-md border border-ink-700 px-2 py-1 text-xs text-ink-300">
          <Headset size={14} aria-hidden />
          A person will follow up
        </p>
      )}
    </li>
  );
}

// A reply written by a person on the support team.
export function HumanMessage({ text }) {
  return (
    <li className="flex flex-col gap-2 rounded-xl border border-signal-dim bg-ink-900 px-4 py-3">
      <p className="flex items-center gap-2 text-xs text-signal">
        <Headset size={14} weight="bold" aria-hidden />
        Support team
      </p>
      <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-ink-100">{text}</p>
    </li>
  );
}
