import { CaretDown, Check, CircleNotch, X } from "@phosphor-icons/react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";

// Seconds since the run started, ticking while it runs and frozen after.
function useElapsed(startedAt, running, finalSeconds) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (!running) return undefined;
    const timer = setInterval(() => setNow(Date.now()), 100);
    return () => clearInterval(timer);
  }, [running]);

  if (!running && finalSeconds != null) return finalSeconds;
  return Math.max(0, (now - startedAt) / 1000);
}

function StepIcon({ status }) {
  if (status === "running") return <CircleNotch size={14} weight="bold" className="animate-spin text-signal" aria-label="in progress" />;
  if (status === "failed") return <X size={14} weight="bold" className="text-alert" aria-label="failed" />;
  return <Check size={14} weight="bold" className="text-signal" aria-label="done" />;
}

// detailed=false is the customer version: plain steps, no agent names or timings.
export default function ActivityTrace({ run, detailed = true }) {
  const reduce = useReducedMotion();
  const running = run.status === "running";
  const elapsed = useElapsed(run.startedAt, running, run.elapsed);

  // Open while it works and fold away when it finishes. Once the visitor
  // toggles it themselves, their choice wins.
  const [manual, setManual] = useState(null);
  const open = manual ?? running;

  const current = [...run.steps].reverse().find((step) => step.status === "running");
  const summary = running
    ? (current?.label ?? "Working")
    : `${run.status === "error" ? "Stopped after" : "Worked for"} ${elapsed.toFixed(1)}s${detailed ? `, ${run.steps.length} steps` : ""}`;

  return (
    <div className="rounded-xl border border-ink-700 bg-ink-900">
      <button
        type="button"
        onClick={() => setManual(!open)}
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-4 py-3 text-left"
      >
        {running ? (
          <CircleNotch size={16} weight="bold" className="animate-spin text-signal" aria-hidden />
        ) : run.status === "error" ? (
          <X size={16} weight="bold" className="text-alert" aria-hidden />
        ) : (
          <Check size={16} weight="bold" className="text-signal" aria-hidden />
        )}
        <span className="flex-1 truncate text-sm text-ink-100">{summary}</span>
        {running && <span className="font-mono text-xs text-ink-300">{elapsed.toFixed(1)}s</span>}
        <CaretDown
          size={14}
          aria-hidden
          className={`text-ink-300 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
        />
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={reduce ? false : { height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={reduce ? { opacity: 0 } : { height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <ol className="flex flex-col gap-2 border-t border-ink-700 px-4 py-3">
              {run.steps.map((step) => (
                <motion.li
                  key={step.id}
                  initial={reduce ? false : { opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex items-center gap-3 text-sm"
                >
                  <StepIcon status={step.status} />
                  <span className={step.status === "running" ? "text-ink-100" : "text-ink-300"}>{step.label}</span>
                  {detailed && step.agent && (
                    <span className="rounded-md border border-ink-700 px-1.5 py-0.5 font-mono text-[10px] text-ink-300">
                      {step.agent}
                    </span>
                  )}
                  {detailed && <span className="ml-auto font-mono text-xs text-ink-500">{step.t.toFixed(1)}s</span>}
                </motion.li>
              ))}
            </ol>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
