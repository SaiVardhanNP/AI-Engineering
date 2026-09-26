import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { CaretDown, WarningCircle } from "@phosphor-icons/react";

const enter = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 120, damping: 20 },
};

function Sources({ sources }) {
  const [open, setOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium text-zinc-600 transition hover:bg-zinc-200/70 dark:text-zinc-400 dark:hover:bg-zinc-800"
      >
        {sources.length}&nbsp;passages used
        <CaretDown size={12} weight="regular" aria-hidden="true" className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.ol
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2 }}
            className="mt-2 divide-y divide-zinc-200 rounded-2xl border border-zinc-200 bg-zinc-50 dark:divide-zinc-800 dark:border-zinc-800 dark:bg-zinc-900"
          >
            {sources.map((source, index) => (
              <li key={index} className="p-4">
                <p className="mb-1 font-mono text-xs text-zinc-600 dark:text-zinc-400">
                  {typeof source.page === "number" ? `Page ${source.page + 1}` : `Passage ${index + 1}`}
                </p>
                <p className="line-clamp-6 whitespace-pre-wrap wrap-break-word text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
                  {source.text}
                </p>
              </li>
            ))}
          </motion.ol>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function Message({ message, onRetry }) {
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

  return (
    <motion.div {...enter}>
      <p className="max-w-[65ch] whitespace-pre-wrap wrap-break-word text-[15px] leading-relaxed">{message.content}</p>
      <Sources sources={message.sources} />
    </motion.div>
  );
}
