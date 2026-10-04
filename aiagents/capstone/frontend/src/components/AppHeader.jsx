import { Headset } from "@phosphor-icons/react";
import { NavLink } from "react-router-dom";

import { USE_MOCK } from "../lib/stream.js";

const tabClass = ({ isActive }) =>
  `rounded-xl px-3 py-1.5 text-sm transition-colors ${
    isActive ? "bg-ink-800 text-ink-100" : "text-ink-300 hover:text-ink-100"
  }`;

export default function AppHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-ink-700 bg-ink-950/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-4 px-4">
        <span className="flex items-center gap-2 text-sm font-medium text-ink-100">
          <Headset size={18} weight="bold" className="text-signal" aria-hidden />
          Supportdesk
        </span>

        <nav aria-label="View" className="flex items-center gap-1">
          <NavLink to="/desk" className={tabClass}>
            Customer view
          </NavLink>
          <NavLink to="/team" className={tabClass}>
            Team view
          </NavLink>
        </nav>

        <span className="hidden w-32 justify-end sm:flex">
          {USE_MOCK && (
            <span className="rounded-md border border-ink-700 px-2 py-1 font-mono text-[11px] text-ink-300">
              Simulated stream
            </span>
          )}
        </span>
      </div>
    </header>
  );
}
