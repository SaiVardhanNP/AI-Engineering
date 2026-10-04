import { Plus } from "@phosphor-icons/react";
import { useReducedMotion } from "motion/react";
import { useEffect, useRef } from "react";

import AppHeader from "../components/AppHeader.jsx";
import Composer from "../components/Composer.jsx";
import CustomerPicker from "../components/CustomerPicker.jsx";
import { AssistantMessage, HumanMessage, RestoredAssistantMessage, UserMessage } from "../components/Message.jsx";
import { useDesk } from "../hooks/useDesk.js";
import { CUSTOMERS } from "../lib/customers.js";

function EmptyState({ customer, onUseSample }) {
  return (
    <div className="flex flex-1 flex-col items-start justify-center gap-4 py-16">
      <h1 className="text-2xl font-medium tracking-tight text-ink-100">How can we help, {customer.name.split(" ")[0]}?</h1>
      <p className="max-w-[60ch] text-sm leading-relaxed text-ink-300">
        Describe the problem and our assistant will look at your account, your recent errors and our
        documentation before it replies.
      </p>
      <button
        type="button"
        onClick={onUseSample}
        className="flex flex-col items-start gap-1 rounded-xl border border-ink-700 bg-ink-900 px-4 py-3 text-left transition hover:border-ink-500 active:scale-[0.98]"
      >
        <span className="text-sm text-ink-100">Try a sample ticket</span>
        <span className="max-w-[60ch] text-xs leading-snug text-ink-300">{customer.starter}</span>
      </button>
    </div>
  );
}

function RestoringSkeleton() {
  return (
    <div className="flex flex-1 flex-col gap-4 py-8" aria-label="Loading your conversation">
      <div className="ml-auto h-10 w-2/5 animate-pulse rounded-xl bg-ink-900" />
      <div className="h-16 w-4/5 animate-pulse rounded-xl bg-ink-900" />
    </div>
  );
}

export default function Desk() {
  const desk = useDesk();
  const reduce = useReducedMotion();
  const endRef = useRef(null);

  const customer = CUSTOMERS.find((c) => c.id === desk.customerId);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "end" });
  }, [desk.messages, reduce]);

  const lastIndex = desk.messages.length - 1;

  function renderMessage(message, index) {
    if (message.role === "user") return <UserMessage key={message.id} text={message.text} />;
    if (message.role === "human") return <HumanMessage key={message.id} text={message.text} />;
    if (message.restored) return <RestoredAssistantMessage key={message.id} restored={message.restored} />;

    return (
      <AssistantMessage
        key={message.id}
        run={message.run}
        canRetry={index === lastIndex && !!desk.lastUserText}
        onRetry={() => desk.send(desk.lastUserText)}
      />
    );
  }

  return (
    <div className="min-h-dvh">
      <AppHeader />

      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <section className="flex min-h-[calc(100dvh-8.5rem)] flex-col" aria-label="Conversation">
          {desk.restoring ? (
            <RestoringSkeleton />
          ) : desk.messages.length === 0 ? (
            <EmptyState customer={customer} onUseSample={() => desk.send(customer.starter)} />
          ) : (
            <ol className="flex flex-1 flex-col gap-6 pb-6">{desk.messages.map(renderMessage)}</ol>
          )}

          <div ref={endRef} />

          <div className="sticky bottom-0 flex flex-col gap-2 bg-ink-950 pb-4 pt-2">
            {desk.waitingForHuman && (
              <p className="text-xs leading-relaxed text-ink-300" role="status">
                A person on our team has your ticket. You can keep writing here, and their reply will appear
                in this conversation.
              </p>
            )}

            {desk.messages.length > 0 && (
              <button
                type="button"
                onClick={desk.newConversation}
                disabled={desk.busy}
                className="flex w-fit items-center gap-1.5 whitespace-nowrap rounded-xl px-2 py-1 text-xs text-ink-300 transition-colors hover:text-ink-100 disabled:opacity-40"
              >
                <Plus size={12} weight="bold" aria-hidden />
                New conversation
              </button>
            )}

            <Composer disabled={desk.busy || desk.restoring} onSend={desk.send} />
          </div>
        </section>

        <aside className="flex flex-col gap-3 lg:sticky lg:top-20 lg:self-start" aria-label="Demo controls">
          <h2 className="text-sm font-medium text-ink-100">Demo controls</h2>
          <p className="text-xs leading-relaxed text-ink-300">
            A real customer would be signed in. Here you pick who you are, and each person has different
            data behind them.
          </p>
          <CustomerPicker value={desk.customerId} onChange={desk.selectCustomer} />
        </aside>
      </div>
    </div>
  );
}
