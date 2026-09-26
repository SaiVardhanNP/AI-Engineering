import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { CaretDown, Check } from "@phosphor-icons/react";

function statusHint(provider) {
  if (provider.status === "no_key") return `Add ${provider.env} to backend/.env to enable.`;
  if (provider.status === "unreachable") return "The model list could not be loaded. Check your connection.";
  return null;
}

function MenuBody({ catalog, value, onPick, menuRef, onKeyDown }) {
  return (
    <div
      ref={menuRef}
      role="menu"
      aria-label="Choose a model"
      onKeyDown={onKeyDown}
      className="w-80 max-w-[calc(100vw-2rem)] rounded-2xl border border-zinc-200 bg-zinc-50 p-2 shadow-xl shadow-emerald-950/10 dark:border-zinc-800 dark:bg-zinc-900 dark:shadow-black/40"
    >
      {catalog.providers.map((provider) => {
        const models = catalog.models.filter((model) => model.provider === provider.id);
        const hint = statusHint(provider);

        return (
          <div key={provider.id} className="px-1 pb-2 pt-1 first:pt-0">
            <p className="flex items-center justify-between px-2 py-1.5 text-xs text-zinc-600 dark:text-zinc-400">
              <span translate="no">{provider.label}</span>
              <span className="font-mono">{provider.cloud ? "Cloud" : "Local"}</span>
            </p>

            {hint && <p className="px-2 pb-1 text-xs text-zinc-600 dark:text-zinc-400">{hint}</p>}

            {models.map((model) => {
              const selected = model.id === value;

              return (
                <button
                  key={model.id}
                  type="button"
                  role="menuitemradio"
                  aria-checked={selected}
                  onClick={() => onPick(model.id)}
                  className={`flex w-full items-center gap-3 rounded-xl px-2 py-2 text-left text-sm transition ${
                    selected ? "bg-zinc-200/80 dark:bg-zinc-800" : "hover:bg-zinc-200/50 dark:hover:bg-zinc-800/60"
                  }`}
                >
                  <span className="min-w-0 flex-1">
                    <span translate="no" className="block truncate font-medium">
                      {model.label}
                    </span>
                    {model.note && (
                      <span className="block text-xs text-zinc-600 dark:text-zinc-400">{model.note}</span>
                    )}
                  </span>
                  {selected && (
                    <Check size={16} weight="regular" aria-hidden="true" className="shrink-0 text-emerald-700 dark:text-emerald-400" />
                  )}
                </button>
              );
            })}
          </div>
        );
      })}

      <p className="border-t border-zinc-200 px-3 pb-2 pt-3 text-xs leading-relaxed text-zinc-600 dark:border-zinc-800 dark:text-zinc-400">
        Cloud models receive your question, your recent messages and the passages found in the document. Your PDF
        itself stays on this machine.
      </p>
    </div>
  );
}

export default function ModelMenu({ catalog, value, onChange, disabled = false, inline = false }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const buttonRef = useRef(null);
  const menuRef = useRef(null);

  const selected = catalog.models.find((model) => model.id === value) || catalog.models[0];

  useEffect(() => {
    if (!open || inline) return undefined;

    function onPointerDown(event) {
      if (rootRef.current && !rootRef.current.contains(event.target)) setOpen(false);
    }

    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open, inline]);

  useEffect(() => {
    if (!open || inline || !menuRef.current) return;
    const target =
      menuRef.current.querySelector('[aria-checked="true"]') ||
      menuRef.current.querySelector('[role="menuitemradio"]');
    if (target) target.focus();
  }, [open, inline]);

  function pick(id) {
    onChange(id);
    if (!inline) {
      setOpen(false);
      if (buttonRef.current) buttonRef.current.focus();
    }
  }

  function onMenuKeyDown(event) {
    const items = [...menuRef.current.querySelectorAll('[role="menuitemradio"]')];
    const index = items.indexOf(document.activeElement);

    if (event.key === "ArrowDown") {
      event.preventDefault();
      items[(index + 1) % items.length].focus();
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      items[(index - 1 + items.length) % items.length].focus();
    } else if (event.key === "Home") {
      event.preventDefault();
      items[0].focus();
    } else if (event.key === "End") {
      event.preventDefault();
      items[items.length - 1].focus();
    } else if (event.key === "Escape" && !inline) {
      event.preventDefault();
      setOpen(false);
      if (buttonRef.current) buttonRef.current.focus();
    } else if (event.key === "Tab" && !inline) {
      setOpen(false);
    }
  }

  if (inline) {
    return <MenuBody catalog={catalog} value={value} onPick={pick} menuRef={menuRef} onKeyDown={onMenuKeyDown} />;
  }

  return (
    <div ref={rootRef} className="relative inline-block">
      <button
        ref={buttonRef}
        type="button"
        disabled={disabled}
        onClick={() => setOpen((current) => !current)}
        aria-haspopup="menu"
        aria-expanded={open}
        className="inline-flex items-center gap-2 rounded-full border border-zinc-300 px-3 py-1.5 text-xs font-medium transition hover:bg-zinc-200/70 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60 dark:border-zinc-700 dark:hover:bg-zinc-800"
      >
        <span className="text-zinc-600 dark:text-zinc-400">Model</span>
        <span translate="no">{selected.label}</span>
        <span className="font-mono text-zinc-600 dark:text-zinc-400">{selected.cloud ? "Cloud" : "Local"}</span>
        <CaretDown
          size={12}
          weight="regular"
          aria-hidden="true"
          className={`transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.16 }}
            style={{ transformOrigin: "bottom left" }}
            className="absolute bottom-full left-0 z-30 mb-2"
          >
            <MenuBody catalog={catalog} value={value} onPick={pick} menuRef={menuRef} onKeyDown={onMenuKeyDown} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
