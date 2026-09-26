import { useEffect, useRef, useState } from "react";
import { ArrowUp, ArrowCounterClockwise, FilePdf } from "@phosphor-icons/react";
import Message from "./Message.jsx";

const STARTERS = [
  "Summarize this document in a few sentences.",
  "What are the main topics it covers?",
  "List the names, tools or dates it mentions.",
];

function Thinking() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setSeconds((value) => value + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div role="status" className="max-w-[65ch]">
      <div className="space-y-2.5" aria-hidden="true">
        {["w-full", "w-11/12", "w-2/3"].map((width) => (
          <div key={width} className={`h-3.5 ${width} animate-pulse rounded-full bg-zinc-200 motion-reduce:animate-none dark:bg-zinc-800`} />
        ))}
      </div>
      <p className="mt-3 text-xs text-zinc-600 dark:text-zinc-400">
        Working on it… <span className="font-mono tabular-nums">{seconds}s</span>. A local model on a CPU
        usually needs about 30&nbsp;seconds.
      </p>
    </div>
  );
}

function NoDocument() {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center px-5 py-16">
      <FilePdf size={40} weight="regular" aria-hidden="true" className="mb-6 text-zinc-500 dark:text-zinc-400" />
      <h2 className="text-3xl font-semibold leading-tight tracking-tight text-balance md:text-4xl">Bring in a PDF</h2>
      <p className="mt-3 max-w-[48ch] text-base leading-relaxed text-zinc-600 dark:text-zinc-400">
        Upload one on the left. Embedding and answering both run on this machine, so the file never leaves it.
      </p>
    </div>
  );
}

function EmptyThread({ onAsk, disabled }) {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center px-5 py-16">
      <h2 className="text-3xl font-semibold leading-tight tracking-tight text-balance md:text-4xl">What Do You Want to Know?</h2>
      <p className="mt-3 max-w-[48ch] text-base leading-relaxed text-zinc-600 dark:text-zinc-400">
        Answers come from this document only, and each reply shows the passages it used.
      </p>
      <ul className="mt-8 max-w-[52ch] divide-y divide-zinc-200 border-y border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
        {STARTERS.map((starter) => (
          <li key={starter}>
            <button
              type="button"
              disabled={disabled}
              onClick={() => onAsk(starter)}
              className="w-full px-1 py-3.5 text-left text-[15px] transition hover:text-emerald-700 disabled:opacity-60 dark:hover:text-emerald-400"
            >
              {starter}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Composer({ document, onAsk, busy }) {
  const [value, setValue] = useState("");
  const fieldRef = useRef(null);

  function submit() {
    const question = value.trim();
    if (!question || busy) return;
    onAsk(question);
    setValue("");
    if (fieldRef.current) fieldRef.current.style.height = "auto";
  }

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        submit();
      }}
      className="mx-auto w-full max-w-3xl px-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] pt-3"
    >
      <div className="flex items-end gap-2 rounded-2xl border border-zinc-300 bg-zinc-50 p-2 transition focus-within:border-emerald-700 focus-within:ring-2 focus-within:ring-emerald-700/30 dark:border-zinc-700 dark:bg-zinc-900 dark:focus-within:border-emerald-400 dark:focus-within:ring-emerald-400/30">
        <label htmlFor="question" className="sr-only">
          Question about {document.filename}
        </label>
        <textarea
          ref={fieldRef}
          id="question"
          name="question"
          autoComplete="off"
          rows={1}
          value={value}
          placeholder={`Ask about ${document.filename}…`}
          onChange={(event) => {
            setValue(event.target.value);
            event.target.style.height = "auto";
            event.target.style.height = `${Math.min(event.target.scrollHeight, 160)}px`;
          }}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              submit();
            }
          }}
          className="max-h-40 min-h-10 flex-1 resize-none bg-transparent px-3 py-2 text-[15px] leading-relaxed outline-none placeholder:text-zinc-500 dark:placeholder:text-zinc-500"
        />
        <button
          type="submit"
          disabled={busy}
          aria-label="Send question"
          className="grid size-10 shrink-0 place-items-center rounded-full bg-emerald-700 text-emerald-50 transition hover:bg-emerald-800 active:scale-[0.96] disabled:cursor-not-allowed disabled:opacity-40 dark:bg-emerald-400 dark:text-emerald-950 dark:hover:bg-emerald-300"
        >
          <ArrowUp size={18} weight="regular" aria-hidden="true" />
        </button>
      </div>
      <p className="mt-2 px-1 text-xs text-zinc-600 dark:text-zinc-400">
        Enter sends. Shift and Enter adds a new line.
      </p>
    </form>
  );
}

export default function Chat({ document, messages, busy, onAsk, onRetry, onReset }) {
  const endRef = useRef(null);
  const [confirmingReset, setConfirmingReset] = useState(false);

  useEffect(() => {
    if (!confirmingReset) return undefined;
    const timer = setTimeout(() => setConfirmingReset(false), 4000);
    return () => clearTimeout(timer);
  }, [confirmingReset]);

  useEffect(() => {
    setConfirmingReset(false);
  }, [document && document.doc_id]);

  useEffect(() => {
    if (endRef.current) endRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, busy]);

  if (!document) return <NoDocument />;

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <header className="flex items-center justify-between gap-4 border-b border-zinc-200 px-5 py-3 dark:border-zinc-800">
        <div className="min-w-0">
          <h2 translate="no" className="truncate text-sm font-medium">{document.filename}</h2>
          <p className="font-mono text-xs tabular-nums text-zinc-600 dark:text-zinc-400">
            {document.chunks}&nbsp;passages indexed
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            if (!confirmingReset) {
              setConfirmingReset(true);
              return;
            }
            setConfirmingReset(false);
            onReset();
          }}
          disabled={busy || messages.length === 0}
          className={`inline-flex shrink-0 items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 ${
            confirmingReset
              ? "border-rose-700 bg-rose-700 text-rose-50 hover:bg-rose-800 dark:border-rose-300 dark:bg-rose-300 dark:text-rose-950 dark:hover:bg-rose-200"
              : "border-zinc-300 hover:bg-zinc-200/70 dark:border-zinc-700 dark:hover:bg-zinc-800"
          }`}
        >
          <ArrowCounterClockwise size={16} weight="regular" aria-hidden="true" />
          {confirmingReset ? "Clear This Chat?" : "New Chat"}
        </button>
      </header>

      {messages.length === 0 && !busy ? (
        <EmptyThread onAsk={onAsk} disabled={busy} />
      ) : (
        <div className="min-h-0 flex-1 overflow-y-auto">
          <div aria-live="polite" className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-5 py-8">
            {messages.map((message, index) => (
              <Message
                key={index}
                message={message}
                onRetry={message.role === "error" && index === messages.length - 1 ? onRetry : undefined}
              />
            ))}
            {busy && <Thinking />}
            <div ref={endRef} />
          </div>
        </div>
      )}

      <Composer key={document.doc_id} document={document} onAsk={onAsk} busy={busy} />
    </div>
  );
}
