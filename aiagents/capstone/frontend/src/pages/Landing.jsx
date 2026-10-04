import { ArrowRight, Headset } from "@phosphor-icons/react";
import { motion, useReducedMotion } from "motion/react";
import { Link } from "react-router-dom";

import { CategoryChips, StatusBadge } from "../components/Badges.jsx";
import ActivityTrace from "../components/ActivityTrace.jsx";
import EvidenceReply from "../components/EvidenceReply.jsx";
import LiveCrewDemo from "../components/LiveCrewDemo.jsx";
import { SAMPLE_TICKET } from "../lib/sampleTicket.js";

const TRY = "Try the demo";

function Reveal({ children, className = "", delay = 0 }) {
  const reduce = useReducedMotion();

  return (
    <motion.div
      initial={reduce ? false : { opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.25 }}
      transition={{ duration: 0.6, delay, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

function PrimaryLink({ to, children }) {
  return (
    <Link
      to={to}
      className="flex w-fit items-center gap-2 whitespace-nowrap rounded-xl bg-signal px-5 py-3 text-sm font-medium text-ink-950 transition active:scale-[0.98] hover:brightness-110"
    >
      {children}
      <ArrowRight size={16} weight="bold" aria-hidden />
    </Link>
  );
}

function Nav() {
  return (
    <header className="border-b border-ink-700">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
        <span className="flex items-center gap-2 text-sm font-medium text-ink-100">
          <Headset size={18} weight="bold" className="text-signal" aria-hidden />
          Supportdesk
        </span>
        <Link
          to="/desk"
          className="whitespace-nowrap rounded-xl border border-ink-700 px-4 py-2 text-sm text-ink-100 transition hover:border-ink-500 active:scale-[0.98]"
        >
          {TRY}
        </Link>
      </div>
    </header>
  );
}

function Hero() {
  const reduce = useReducedMotion();

  return (
    <section className="mx-auto grid min-h-[calc(100dvh-4rem)] max-w-7xl items-center gap-12 px-4 py-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)]">
      <motion.div
        initial={reduce ? false : { opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="flex flex-col gap-6"
      >
        <h1 className="text-5xl font-medium leading-[1.05] tracking-tighter text-ink-100 md:text-6xl">
          Support that shows its work.
        </h1>
        <p className="max-w-[44ch] text-lg leading-relaxed text-ink-300">
          An AI crew reads the customer&apos;s account and your docs, replies, and proves every claim.
        </p>
        <div className="flex flex-wrap items-center gap-3">
          <PrimaryLink to="/desk">{TRY}</PrimaryLink>
          <Link
            to="/team"
            className="whitespace-nowrap rounded-xl border border-ink-700 px-5 py-3 text-sm text-ink-100 transition hover:border-ink-500 active:scale-[0.98]"
          >
            See the team view
          </Link>
        </div>
      </motion.div>

      <motion.div
        initial={reduce ? false : { opacity: 0, y: 28 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
      >
        <LiveCrewDemo />
      </motion.div>
    </section>
  );
}

const FLOW = [
  {
    title: "Read",
    body: "The router decides if a ticket is about billing, the account, a technical error, or a mix of them.",
  },
  {
    title: "Investigate",
    body: "Specialists look up payments, subscription state, error logs and your documentation. Independent ones work at the same time.",
  },
  {
    title: "Draft",
    body: "A responder writes the reply from those findings and nothing else.",
  },
  {
    title: "Verify",
    body: "An evaluator lists every claim with a quote from the findings. Then code checks that each quote really exists.",
  },
];

function Flow() {
  return (
    <section className="mx-auto grid max-w-7xl gap-12 px-4 py-28 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
      <Reveal className="lg:sticky lg:top-24 lg:self-start">
        <h2 className="text-3xl font-medium leading-tight tracking-tight text-ink-100 md:text-4xl">
          Six agents work every ticket.
        </h2>
      </Reveal>

      <ol className="flex flex-col gap-14">
        {FLOW.map((item, index) => (
          <Reveal key={item.title} delay={index * 0.05}>
            <li className="flex flex-col gap-2">
              <h3 className="text-2xl font-medium tracking-tight text-ink-100">{item.title}</h3>
              <p className="max-w-[56ch] text-base leading-relaxed text-ink-300">{item.body}</p>
            </li>
          </Reveal>
        ))}
      </ol>
    </section>
  );
}

function Receipts() {
  return (
    <section className="bg-ink-900 py-28">
      <div className="mx-auto flex max-w-7xl flex-col gap-10 px-4">
        <Reveal className="flex flex-col gap-3">
          <h2 className="max-w-[20ch] text-3xl font-medium leading-tight tracking-tight text-ink-100 md:text-4xl">
            Hover a sentence. See the proof.
          </h2>
          <p className="max-w-[60ch] text-base leading-relaxed text-ink-300">
            Every claim in a reply links to the exact words it came from. This is a reply recorded from a
            real run for a fictional customer.
          </p>
        </Reveal>

        <Reveal delay={0.1}>
          <EvidenceReply text={SAMPLE_TICKET.reply} claims={SAMPLE_TICKET.claims} findings={SAMPLE_TICKET.findings} />
        </Reveal>
      </div>
    </section>
  );
}

const SAMPLE_RUN = {
  status: "done",
  startedAt: 0,
  elapsed: 14.2,
  reply: SAMPLE_TICKET.reply,
  ticketId: null,
  error: null,
  categories: SAMPLE_TICKET.categories,
  agents: {},
  steps: [
    { id: 0, kind: "tool", label: "Checking your payments", status: "done", t: 3.1 },
    { id: 1, kind: "tool", label: "Reading your recent error logs", status: "done", t: 3.1 },
    { id: 2, kind: "tool", label: "Searching the documentation", status: "done", t: 3.4 },
    { id: 3, kind: "tool", label: "Checking your subscription status", status: "done", t: 11.8 },
    { id: 4, kind: "stage", label: "Checking the reply against what we found", status: "done", t: 12.4 },
  ],
};

const SAMPLE_QUEUE = [
  { customer: "Frank Nair", message: "I was charged twice last month and I want a refund.", categories: ["billing"], status: "replied", review: "none" },
  { customer: "Dan Iyer", message: "Why was my last invoice $61.40 when the plan is $25?", categories: ["billing"], status: "escalated", review: "open" },
];

function Views() {
  return (
    <section className="mx-auto flex max-w-7xl flex-col gap-10 px-4 py-28">
      <Reveal>
        <h2 className="max-w-[24ch] text-3xl font-medium leading-tight tracking-tight text-ink-100 md:text-4xl">
          Customers get answers. Your team gets the receipts.
        </h2>
      </Reveal>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <Reveal className="flex flex-col gap-4 rounded-xl border border-ink-700 bg-ink-900 p-6">
          <h3 className="text-sm font-medium text-ink-100">What the customer sees</h3>
          <ActivityTrace run={SAMPLE_RUN} detailed={false} />
          <p className="whitespace-pre-wrap px-1 text-sm leading-relaxed text-ink-100">
            {SAMPLE_TICKET.reply.split("\n\n")[1].split(". ").slice(0, 2).join(". ") + "."}
          </p>
        </Reveal>

        <Reveal delay={0.1} className="flex flex-col gap-4 rounded-xl border border-ink-700 bg-ink-900 p-6">
          <h3 className="text-sm font-medium text-ink-100">What your team sees</h3>
          <ul className="flex flex-col gap-3">
            {SAMPLE_QUEUE.map((ticket) => (
              <li key={ticket.customer} className="flex flex-col gap-2 rounded-xl border border-ink-700 bg-ink-950 p-3">
                <span className="flex items-center justify-between gap-2">
                  <span className="text-sm text-ink-100">{ticket.customer}</span>
                  <StatusBadge ticket={ticket} />
                </span>
                <span className="text-xs leading-relaxed text-ink-300">{ticket.message}</span>
                <CategoryChips categories={ticket.categories} />
              </li>
            ))}
          </ul>
          <p className="text-xs leading-relaxed text-ink-300">
            Open any ticket to read the findings, every draft, and the evidence behind each claim.
          </p>
        </Reveal>
      </div>
    </section>
  );
}

const LIMITS = [
  {
    lead: "It will not look up anyone else's account.",
    body: "The customer is fixed inside the tools from the session. The model has no way to change it.",
  },
  {
    lead: "It will not promise what it cannot do.",
    body: "Dates, timelines and finished actions that are not in the findings are rejected before a reply goes out.",
  },
  {
    lead: "It will not guess when it is unsure.",
    body: "After two failed rewrites, a person gets the ticket with the draft and the reasons attached.",
  },
];

function Limits() {
  return (
    <section className="bg-ink-900 py-28">
      <div className="mx-auto flex max-w-4xl flex-col gap-14 px-4">
        {LIMITS.map((item, index) => (
          <Reveal key={item.lead} delay={index * 0.05} className="flex flex-col gap-3">
            <h2 className="text-2xl font-medium leading-snug tracking-tight text-ink-100 md:text-3xl">{item.lead}</h2>
            <p className="max-w-[56ch] text-base leading-relaxed text-ink-300">{item.body}</p>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

function Closing() {
  return (
    <section className="mx-auto flex max-w-7xl flex-col items-start gap-6 px-4 py-28">
      <Reveal className="flex flex-col gap-6">
        <h2 className="max-w-[18ch] text-4xl font-medium leading-tight tracking-tight text-ink-100 md:text-5xl">
          Open it and send a ticket.
        </h2>
        <PrimaryLink to="/desk">{TRY}</PrimaryLink>
      </Reveal>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-ink-700">
      <p className="mx-auto max-w-7xl px-4 py-8 text-xs leading-relaxed text-ink-300">
        Built with CrewAI, FastAPI, Gemini, Pinecone and React. Every customer and every record in the demo is
        fictional.
      </p>
    </footer>
  );
}

export default function Landing() {
  return (
    <div className="min-h-dvh">
      <Nav />
      <main>
        <Hero />
        <Flow />
        <Receipts />
        <Views />
        <Limits />
        <Closing />
      </main>
      <Footer />
    </div>
  );
}
