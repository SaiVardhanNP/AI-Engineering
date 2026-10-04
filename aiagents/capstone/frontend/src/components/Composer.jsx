import { PaperPlaneRight } from "@phosphor-icons/react";
import { useState } from "react";

export default function Composer({ disabled, onSend }) {
  const [text, setText] = useState("");

  function submit() {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  }

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        submit();
      }}
      className="flex items-end gap-3 rounded-xl border border-ink-700 bg-ink-900 p-3 focus-within:border-ink-500"
    >
      <label htmlFor="ticket-message" className="sr-only">
        Describe your problem
      </label>
      <textarea
        id="ticket-message"
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit();
          }
        }}
        rows={2}
        maxLength={2000}
        placeholder="Describe the problem. Press Enter to send."
        className="max-h-40 min-h-12 flex-1 resize-none bg-transparent text-sm leading-relaxed text-ink-100 outline-none placeholder:text-ink-500"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="flex shrink-0 items-center gap-2 whitespace-nowrap rounded-xl bg-signal px-4 py-2 text-sm font-medium text-ink-950 transition active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
      >
        <PaperPlaneRight size={16} weight="bold" aria-hidden />
        Send
      </button>
    </form>
  );
}
