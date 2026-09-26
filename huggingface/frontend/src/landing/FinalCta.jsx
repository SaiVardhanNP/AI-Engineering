import { Link } from "react-router-dom";
import { ArrowRight } from "@phosphor-icons/react";
import Reveal from "./Reveal.jsx";

export default function FinalCta() {
  return (
    <section className="border-t border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mx-auto grid max-w-7xl items-center gap-12 px-5 py-24 md:px-8 md:py-32 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <Reveal>
          <h2 className="max-w-[14ch] text-4xl font-semibold leading-tight tracking-tight text-balance md:text-5xl">
            Try It on Your Own PDF
          </h2>
          <p className="mt-5 max-w-[46ch] text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
            Start the two servers below, open Folio, and drop in a file.
          </p>
          <Link
            to="/app"
            className="mt-8 inline-flex items-center gap-2 rounded-full bg-emerald-700 px-6 py-3 text-base font-medium text-emerald-50 transition hover:bg-emerald-800 active:scale-[0.98] dark:bg-emerald-400 dark:text-emerald-950 dark:hover:bg-emerald-300"
          >
            Open Folio
            <ArrowRight size={18} weight="regular" aria-hidden="true" />
          </Link>
        </Reveal>

        <Reveal delay={0.1}>
          <pre className="overflow-x-auto rounded-2xl bg-zinc-950 p-5 font-mono text-sm leading-7 text-zinc-100 dark:bg-zinc-950 dark:ring-1 dark:ring-zinc-800">
            <code>
              <span className="text-zinc-400"># backend</span>
              {"\n"}
              uvicorn main:app --reload
              {"\n\n"}
              <span className="text-zinc-400"># frontend</span>
              {"\n"}
              npm run dev
            </code>
          </pre>
        </Reveal>
      </div>
    </section>
  );
}
