import { useState } from "react";

export function useTheme() {
  const [theme, setTheme] = useState(() =>
    document.documentElement.classList.contains("dark") ? "dark" : "light",
  );

  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.classList.toggle("dark", next === "dark");
    try {
      localStorage.setItem("theme", next);
    } catch {
      // storage can be blocked; the choice still applies for this visit
    }
    setTheme(next);
  }

  return { theme, toggle };
}
