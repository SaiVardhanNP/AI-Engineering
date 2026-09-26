import { Link } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle.jsx";
import { useTheme } from "../useTheme.js";
import FinalCta from "./FinalCta.jsx";
import Hero from "./Hero.jsx";
import Logos from "./Logos.jsx";
import ModelsSection from "./ModelsSection.jsx";
import Privacy from "./Privacy.jsx";
import Story from "./Story.jsx";

const LINKS = [
  { href: "#how", label: "How It Works" },
  { href: "#models", label: "Models" },
  { href: "#privacy", label: "Privacy" },
];

function Nav({ theme, onToggleTheme }) {
  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200 bg-zinc-100/85 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/80">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-6 px-5 md:px-8">
        <Link to="/" translate="no" className="text-xl font-semibold tracking-tight">
          Folio
        </Link>

        <nav aria-label="Sections" className="hidden items-center gap-8 md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm text-zinc-600 transition hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
          <Link
            to="/app"
            className="inline-flex items-center rounded-full bg-emerald-700 px-5 py-2 text-sm font-medium text-emerald-50 transition hover:bg-emerald-800 active:scale-[0.98] dark:bg-emerald-400 dark:text-emerald-950 dark:hover:bg-emerald-300"
          >
            Open Folio
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Landing() {
  const { theme, toggle } = useTheme();

  return (
    <div className="overflow-x-clip">
      <a
        href="#content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-emerald-700 focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-emerald-50"
      >
        Skip to Content
      </a>
      <Nav theme={theme} onToggleTheme={toggle} />
      <main id="content">
        <Hero />
        <Logos />
        <Story />
        <ModelsSection />
        <Privacy />
        <FinalCta />
      </main>
      <footer className="border-t border-zinc-200 dark:border-zinc-800">
        <div className="mx-auto max-w-7xl px-5 py-8 text-sm text-zinc-600 md:px-8 dark:text-zinc-400">
          Folio runs on your machine. Built with FastAPI, LangChain, Chroma and PDF.js.
        </div>
      </footer>
    </div>
  );
}
