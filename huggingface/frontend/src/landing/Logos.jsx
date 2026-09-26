import { siFastapi, siGooglegemini, siHuggingface, siLangchain, siReact } from "simple-icons";

const LOGOS = [siHuggingface, siGooglegemini, siLangchain, siFastapi, siReact];

export default function Logos() {
  return (
    <section aria-label="Technology behind Folio" className="border-y border-zinc-200 dark:border-zinc-800">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-10 md:flex-row md:items-center md:justify-between md:px-8">
        <p className="text-sm text-zinc-600 dark:text-zinc-400">Runs on</p>
        <ul className="flex flex-wrap items-center gap-x-12 gap-y-6 text-zinc-600 dark:text-zinc-400">
          {LOGOS.map((icon) => (
            <li key={icon.slug}>
              <svg role="img" aria-label={icon.title} viewBox="0 0 24 24" width="28" height="28" className="fill-current">
                <title>{icon.title}</title>
                <path d={icon.path} />
              </svg>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
