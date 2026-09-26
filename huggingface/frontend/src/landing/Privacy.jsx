import Reveal from "./Reveal.jsx";

const ROWS = [
  {
    model: "Gemma 3 1B",
    runs: "On your computer",
    leaves: "Nothing",
    needs: "No key",
  },
  {
    model: "Gemini models",
    runs: "Google servers",
    leaves: "Your question, recent messages and 3 passages",
    needs: "GEMINI_API_KEY",
  },
  {
    model: "Groq models",
    runs: "Groq servers",
    leaves: "Your question, recent messages and 3 passages",
    needs: "GROQ_API_KEY",
  },
];

export default function Privacy() {
  return (
    <section id="privacy" className="scroll-mt-16">
      <div className="mx-auto max-w-7xl px-5 py-24 md:px-8 md:py-32">
        <Reveal>
          <h2 className="max-w-[14ch] text-4xl font-semibold leading-tight tracking-tight text-balance md:text-5xl">
            Local by Default
          </h2>
          <p className="mt-5 max-w-[60ch] text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
            Your PDFs and their index stay on this computer. Only a cloud model you choose receives text, and only the
            text it needs to answer.
          </p>
        </Reveal>

        <Reveal delay={0.1} className="mt-12 overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-[15px]">
            <caption className="sr-only">What each model receives</caption>
            <thead>
              <tr className="text-sm text-zinc-600 dark:text-zinc-400">
                <th scope="col" className="pb-3 pr-6 font-medium">
                  Model
                </th>
                <th scope="col" className="pb-3 pr-6 font-medium">
                  Runs
                </th>
                <th scope="col" className="pb-3 pr-6 font-medium">
                  What it receives
                </th>
                <th scope="col" className="pb-3 font-medium">
                  Needs
                </th>
              </tr>
            </thead>
            <tbody>
              {ROWS.map((row) => (
                <tr key={row.model} className="border-t border-zinc-200 align-top dark:border-zinc-800">
                  <th scope="row" translate="no" className="py-4 pr-6 font-medium">
                    {row.model}
                  </th>
                  <td className="py-4 pr-6 text-zinc-600 dark:text-zinc-400">{row.runs}</td>
                  <td className="py-4 pr-6 text-zinc-600 dark:text-zinc-400">{row.leaves}</td>
                  <td className="py-4 font-mono text-sm">{row.needs}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Reveal>

        <Reveal delay={0.15}>
          <p className="mt-8 max-w-[62ch] text-base leading-relaxed text-zinc-600 dark:text-zinc-400">
            API keys live in <span className="font-mono text-sm">backend/.env</span> and are never sent to the
            browser. A provider without a key stays in the menu with a note on how to enable it.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
