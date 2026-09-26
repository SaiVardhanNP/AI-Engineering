import { useState } from "react";
import ModelMenu from "../components/ModelMenu.jsx";
import Reveal from "./Reveal.jsx";

const SAMPLE = {
  default: "local:gemma-3-1b-it",
  models: [
    { id: "local:gemma-3-1b-it", label: "Gemma 3 1B", provider: "local", cloud: false, note: "Runs offline" },
    { id: "gemini:gemini-3.8-flash", label: "Gemini 3.8 Flash", provider: "gemini", cloud: true, note: null },
    { id: "gemini:gemini-3.1-pro-preview", label: "Gemini 3.1 Pro", provider: "gemini", cloud: true, note: "Preview" },
    { id: "gemini:gemini-3.5-flash-lite", label: "Gemini 3.5 Flash Lite", provider: "gemini", cloud: true, note: null },
    { id: "groq:openai/gpt-oss-120b", label: "GPT OSS 120B", provider: "groq", cloud: true, note: null },
    { id: "groq:qwen/qwen3.8-27b", label: "Qwen3.8 27B", provider: "groq", cloud: true, note: null },
    { id: "groq:openai/gpt-oss-20b", label: "GPT OSS 20B", provider: "groq", cloud: true, note: null },
  ],
  providers: [
    { id: "local", label: "On this machine", cloud: false, env: null, status: "ready" },
    { id: "gemini", label: "Google Gemini", cloud: true, env: "GEMINI_API_KEY", status: "ready" },
    { id: "groq", label: "Groq", cloud: true, env: "GROQ_API_KEY", status: "ready" },
  ],
};

const TIMINGS = [
  { model: "Gemma 3 1B", where: "On your computer", seconds: "29" },
  { model: "Gemini 3.8 Flash", where: "Google", seconds: "7" },
  { model: "GPT OSS 120B", where: "Groq", seconds: "2" },
];

export default function ModelsSection() {
  const [value, setValue] = useState(SAMPLE.default);

  return (
    <section id="models" className="scroll-mt-16 bg-zinc-50 dark:bg-zinc-900">
      <div className="mx-auto max-w-7xl px-5 py-24 md:px-8 md:py-32">
        <Reveal>
          <h2 className="max-w-[16ch] text-4xl font-semibold leading-tight tracking-tight text-balance md:text-5xl">
            One Conversation, Any Model
          </h2>
          <p className="mt-5 max-w-[56ch] text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
            Run a small local model on private files, or a hosted one for harder questions. History and sources stay
            put when you switch.
          </p>
        </Reveal>

        <div className="mt-14 grid items-start gap-14 lg:grid-cols-[auto_minmax(0,1fr)] lg:gap-20">
          <Reveal>
            <p className="mb-3 text-sm text-zinc-600 dark:text-zinc-400">The same menu you get in the app. Try it.</p>
            <ModelMenu catalog={SAMPLE} value={value} onChange={setValue} inline />
          </Reveal>

          <Reveal delay={0.1}>
            <p className="mb-3 text-sm text-zinc-600 dark:text-zinc-400">Speed matters when the question is hard.</p>
            <h3 className="text-xl font-semibold tracking-tight">Time to a Full Answer</h3>
            <div className="mt-4 max-w-xl overflow-x-auto">
              <table className="w-full text-left text-[15px]">
                <caption className="sr-only">Answer time by model on one laptop</caption>
                <thead>
                  <tr className="text-sm text-zinc-600 dark:text-zinc-400">
                    <th scope="col" className="pb-3 pr-6 font-medium">
                      Model
                    </th>
                    <th scope="col" className="pb-3 pr-6 font-medium">
                      Runs on
                    </th>
                    <th scope="col" className="pb-3 text-right font-medium">
                      Seconds
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {TIMINGS.map((row) => (
                    <tr key={row.model} className="border-t border-zinc-200 dark:border-zinc-800">
                      <th scope="row" translate="no" className="py-3 pr-6 font-medium">
                        {row.model}
                      </th>
                      <td className="py-3 pr-6 text-zinc-600 dark:text-zinc-400">{row.where}</td>
                      <td className="py-3 text-right font-mono tabular-nums">{row.seconds}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-4 max-w-[52ch] text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
              Each measured once on a 4-core laptop without a GPU. Your numbers will differ.
            </p>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
