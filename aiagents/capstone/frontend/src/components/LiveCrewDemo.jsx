import { useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";

import { mockStream } from "../lib/mockStream.js";
import { AGENT_KEYS, applyEvent, initialRun } from "../lib/runReducer.js";
import CrewMap from "./CrewMap.jsx";

const PAUSE_BETWEEN_RUNS_MS = 2800;

const wait = (ms, signal) =>
  new Promise((resolve) => {
    // an abort that already happened will not fire its event again
    if (signal.aborted) return resolve();

    const timer = setTimeout(resolve, ms);
    signal.addEventListener("abort", () => {
      clearTimeout(timer);
      resolve();
    });
  });

const FINISHED = Object.fromEntries(AGENT_KEYS.map((key) => [key, "done"]));

// The real crew map driven by the real reducer, replaying a recorded ticket on a loop.
export default function LiveCrewDemo() {
  const reduce = useReducedMotion();
  const [run, setRun] = useState(() => initialRun());

  useEffect(() => {
    if (reduce) return undefined;

    const controller = new AbortController();
    const { signal } = controller;

    (async () => {
      while (!signal.aborted) {
        let current = initialRun();
        setRun(current);

        for await (const event of mockStream({ signal })) {
          current = applyEvent(current, event);
          setRun(current);
        }

        await wait(PAUSE_BETWEEN_RUNS_MS, signal);
      }
    })();

    return () => controller.abort();
  }, [reduce]);

  const running = [...run.steps].reverse().find((step) => step.status === "running");
  const caption = reduce
    ? "Reply checked and sent"
    : run.status === "done"
      ? "Reply checked and sent"
      : (running?.label ?? "Reading the ticket");

  return (
    <figure className="flex flex-col gap-4">
      <div className="rounded-xl border border-ink-700 bg-ink-900 p-5">
        <CrewMap agents={reduce ? FINISHED : run.agents} />
      </div>

      <figcaption className="flex flex-col gap-1">
        <span className="font-mono text-sm text-ink-100" aria-hidden>
          {caption}
        </span>
        <span className="text-xs leading-snug text-ink-300">
          Replaying a recorded ticket: charged twice, subscription inactive, authentication errors.
        </span>
      </figcaption>
    </figure>
  );
}
