import { motion } from "motion/react";
import { WarningCircle } from "@phosphor-icons/react";

const enter = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 120, damping: 20 },
};

const CITATION = /\[(\d+(?:\s*,\s*\d+)*)\]/g;

function CitationChip({ number, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`Open source ${number}`}
      className="mx-0.5 inline-grid size-5 -translate-y-px place-items-center rounded-full bg-emerald-700/10 align-middle text-[11px] font-medium text-emerald-800 transition hover:bg-emerald-700 hover:text-emerald-50 active:scale-[0.94] dark:bg-emerald-400/15 dark:text-emerald-300 dark:hover:bg-emerald-400 dark:hover:text-emerald-950"
    >
      <span className="tabular-nums">{number}</span>
    </button>
  );
}

function AnswerText({ text, sources, onCite }) {
  const nodes = [];
  let last = 0;
  let match;

  CITATION.lastIndex = 0;

  while ((match = CITATION.exec(text)) !== null) {
    const numbers = match[1]
      .split(",")
      .map((value) => parseInt(value.trim(), 10))
      .filter((value) => value >= 1 && value <= sources.length);

    if (numbers.length === 0) continue;

    if (match.index > last) nodes.push(text.slice(last, match.index));

    numbers.forEach((number, index) => {
      nodes.push(<CitationChip key={`${match.index}-${index}`} number={number} onClick={() => onCite(number - 1)} />);
    });

    last = match.index + match[0].length;
  }

  if (last < text.length) nodes.push(text.slice(last));

  return nodes.map((node, index) => (typeof node === "string" ? <span key={`text-${index}`}>{node}</span> : node));
}

function SourceRow({ sources, activeIndex, onCite }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 flex flex-wrap items-center gap-2">
      <span className="text-xs text-zinc-600 dark:text-zinc-400">Sources</span>
      {sources.map((source, index) => (
        <button
          key={index}
          type="button"
          onClick={() => onCite(index)}
          aria-pressed={activeIndex === index}
          className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium transition active:scale-[0.98] ${
            activeIndex === index
              ? "border-emerald-700 bg-emerald-700/10 text-emerald-800 dark:border-emerald-400 dark:bg-emerald-400/15 dark:text-emerald-300"
              : "border-zinc-300 hover:bg-zinc-200/70 dark:border-zinc-700 dark:hover:bg-zinc-800"
          }`}
        >
          <span className="font-mono tabular-nums">{index + 1}</span>
          {typeof source.page === "number" ? `Page ${source.page + 1}` : "Passage"}
        </button>
      ))}
    </div>
  );
}

export default function Message({ message, activeIndex, onRetry, onCite }) {
  if (message.role === "user") {
    return (
      <motion.div {...enter} className="flex justify-end">
        <p className="max-w-[85%] whitespace-pre-wrap wrap-break-word rounded-2xl bg-zinc-200/80 px-4 py-2.5 text-[15px] leading-relaxed dark:bg-zinc-800">
          {message.content}
        </p>
      </motion.div>
    );
  }

  if (message.role === "error") {
    return (
      <motion.div {...enter} role="alert" className="flex max-w-[65ch] items-start gap-3 text-sm text-rose-700 dark:text-rose-300">
        <WarningCircle size={20} weight="regular" aria-hidden="true" className="mt-0.5 shrink-0" />
        <div>
          <p>{message.content}</p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="mt-2 rounded-full border border-rose-700/40 px-3 py-1 text-xs font-medium transition hover:bg-rose-700/10 active:scale-[0.98] dark:border-rose-300/40 dark:hover:bg-rose-300/10"
            >
              Try Again
            </button>
          )}
        </div>
      </motion.div>
    );
  }

  const sources = message.sources || [];

  return (
    <motion.div {...enter}>
      <p className="max-w-[65ch] whitespace-pre-wrap wrap-break-word text-[15px] leading-relaxed">
        <AnswerText text={message.content} sources={sources} onCite={(index) => onCite(sources, index)} />
      </p>
      <SourceRow sources={sources} activeIndex={activeIndex} onCite={(index) => onCite(sources, index)} />
      {message.model && (
        <p className="mt-3 text-xs text-zinc-600 dark:text-zinc-400">
          Answered by <span translate="no">{message.model.label}</span>
        </p>
      )}
    </motion.div>
  );
}
