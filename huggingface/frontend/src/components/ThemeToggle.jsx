import { MoonStars, Sun } from "@phosphor-icons/react";

export default function ThemeToggle({ theme, onToggle }) {
  const Icon = theme === "dark" ? Sun : MoonStars;

  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      className="grid size-9 place-items-center rounded-full text-zinc-600 transition hover:bg-zinc-200 active:scale-[0.96] dark:text-zinc-400 dark:hover:bg-zinc-800"
    >
      <Icon size={18} weight="regular" aria-hidden="true" />
    </button>
  );
}
