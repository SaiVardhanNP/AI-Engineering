import { useRef, useState } from "react";
import { motion } from "motion/react";
import { Check, FilePdf, MoonStars, Sun, UploadSimple } from "@phosphor-icons/react";

function ThemeToggle({ theme, onToggle }) {
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

function UploadZone({ onUpload, uploading }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  function handleFiles(files) {
    const file = files && files[0];
    if (file) onUpload(file);
  }

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        handleFiles(event.dataTransfer.files);
      }}
      className={`rounded-2xl border border-dashed p-4 transition-colors ${
        dragging
          ? "border-emerald-600 bg-emerald-600/10 dark:border-emerald-400 dark:bg-emerald-400/10"
          : "border-zinc-300 dark:border-zinc-700"
      }`}
    >
      <input
        ref={inputRef}
        id="pdf-upload"
        name="file"
        type="file"
        accept="application/pdf,.pdf"
        className="sr-only"
        onChange={(event) => {
          handleFiles(event.target.files);
          event.target.value = "";
        }}
      />
      <p className="text-sm text-zinc-600 dark:text-zinc-400">Drop a PDF here, or pick one from your computer.</p>
      <button
        type="button"
        disabled={uploading}
        onClick={() => inputRef.current && inputRef.current.click()}
        className="mt-3 inline-flex items-center gap-2 rounded-full bg-emerald-700 px-4 py-2 text-sm font-medium text-emerald-50 transition hover:bg-emerald-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-emerald-400 dark:text-emerald-950 dark:hover:bg-emerald-300"
      >
        <UploadSimple size={16} weight="regular" aria-hidden="true" />
        {uploading ? "Indexing…" : "Upload PDF"}
      </button>
    </div>
  );
}

function DocumentRow({ document, active, onSelect }) {
  return (
    <li>
      <button
        type="button"
        onClick={() => onSelect(document.doc_id)}
        aria-current={active ? "true" : undefined}
        className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition ${
          active
            ? "bg-zinc-200/80 dark:bg-zinc-800"
            : "hover:bg-zinc-200/50 dark:hover:bg-zinc-800/60"
        }`}
      >
        <FilePdf size={20} weight="regular" aria-hidden="true" className="shrink-0 text-zinc-500 dark:text-zinc-400" />
        <span className="min-w-0 flex-1">
          <span translate="no" className="block truncate text-sm font-medium">{document.filename}</span>
          <span className="block font-mono text-xs tabular-nums text-zinc-600 dark:text-zinc-400">
            {document.chunks}&nbsp;passages
          </span>
        </span>
        {active && <Check size={16} weight="regular" aria-hidden="true" className="shrink-0 text-emerald-700 dark:text-emerald-400" />}
      </button>
    </li>
  );
}

export default function Sidebar({
  documents,
  activeId,
  onSelect,
  onUpload,
  uploading,
  uploadNote,
  loading,
  serverUp,
  theme,
  onToggleTheme,
}) {
  return (
    <aside className="flex flex-col gap-6 border-b border-zinc-200 bg-zinc-50 p-5 dark:border-zinc-800 dark:bg-zinc-900 lg:h-[100dvh] lg:overflow-y-auto lg:border-b-0 lg:border-r">
      <div className="flex items-center justify-between">
        <h1 translate="no" className="text-xl font-semibold tracking-tight">Folio</h1>
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />
      </div>

      <UploadZone onUpload={onUpload} uploading={uploading} />

      <p role="status" aria-live="polite" className="-mt-3 min-h-5 text-sm text-zinc-600 dark:text-zinc-400">
        {uploading ? "Reading and embedding your file, this can take a minute…" : uploadNote}
      </p>

      <nav aria-label="Documents" className="flex-1">
        <h2 className="mb-2 px-3 text-xs font-medium uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
          Documents
        </h2>

        {loading ? (
          <div className="space-y-2" aria-hidden="true">
            {[0, 1].map((index) => (
              <div key={index} className="h-12 animate-pulse rounded-xl bg-zinc-200 motion-reduce:animate-none dark:bg-zinc-800" />
            ))}
          </div>
        ) : documents.length === 0 ? (
          <p className="px-3 text-sm text-zinc-600 dark:text-zinc-400">
            Nothing indexed yet. Your uploads will be listed here.
          </p>
        ) : (
          <motion.ul layout className="space-y-1">
            {documents.map((document) => (
              <DocumentRow
                key={document.doc_id}
                document={document}
                active={document.doc_id === activeId}
                onSelect={onSelect}
              />
            ))}
          </motion.ul>
        )}
      </nav>

      <p className="flex items-center gap-2 text-xs text-zinc-600 dark:text-zinc-400">
        <span
          aria-hidden="true"
          className={`size-2 rounded-full ${serverUp ? "bg-emerald-600 dark:bg-emerald-400" : "bg-rose-600 dark:bg-rose-400"}`}
        />
        {serverUp ? "Local server connected" : "Local server not reachable"}
      </p>
    </aside>
  );
}
