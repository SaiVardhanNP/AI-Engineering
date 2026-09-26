import { useEffect, useRef, useState } from "react";
import { motion } from "motion/react";
import { X } from "@phosphor-icons/react";
import * as pdfjs from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import { documentFileUrl } from "../api.js";

pdfjs.GlobalWorkerOptions.workerSrc = workerUrl;

const pdfCache = new Map();

function loadPdf(docId) {
  if (!pdfCache.has(docId)) {
    const task = pdfjs.getDocument({ url: documentFileUrl(docId) }).promise;
    task.catch(() => pdfCache.delete(docId));
    pdfCache.set(docId, task);
  }
  return pdfCache.get(docId);
}

const squash = (text) => text.toLowerCase().replace(/[^a-z0-9]+/g, "");

export default function SourcePanel({ docId, filename, sources, activeIndex, onSelect, onClose }) {
  const source = sources[activeIndex];
  const pageNumber = typeof source.page === "number" ? source.page + 1 : 1;

  const frameRef = useRef(null);
  const canvasRef = useRef(null);
  const scrollRef = useRef(null);
  const closeRef = useRef(null);

  const [width, setWidth] = useState(0);
  const [view, setView] = useState({ status: "loading", rects: [], size: null, pages: null });

  useEffect(() => {
    const element = frameRef.current;
    if (!element) return undefined;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.floor(entry.contentRect.width)));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  useEffect(() => {
    if (window.matchMedia("(max-width: 1279px)").matches && closeRef.current) closeRef.current.focus();
  }, []);

  useEffect(() => {
    if (!width) return undefined;

    let cancelled = false;
    let renderTask = null;

    setView((current) => ({ status: "loading", rects: [], size: null, pages: current.pages }));


    (async () => {
      try {
        const pdf = await loadPdf(docId);
        const page = await pdf.getPage(Math.min(pageNumber, pdf.numPages));
        if (cancelled) return;

        const base = page.getViewport({ scale: 1 });
        const scale = width / base.width;
        const viewport = page.getViewport({ scale });
        const ratio = window.devicePixelRatio || 1;

        const canvas = canvasRef.current;
        canvas.width = Math.floor(viewport.width * ratio);
        canvas.height = Math.floor(viewport.height * ratio);
        canvas.style.width = `${Math.floor(viewport.width)}px`;
        canvas.style.height = `${Math.floor(viewport.height)}px`;

        renderTask = page.render({
          canvas,
          viewport,
          transform: ratio !== 1 ? [ratio, 0, 0, ratio, 0, 0] : undefined,
        });
        await renderTask.promise;

        const content = await page.getTextContent();
        if (cancelled) return;

        const target = squash(source.text);
        const rects = [];

        for (const item of content.items) {
          if (!item.str) continue;

          const key = squash(item.str);
          if (key.length < 4 || !target.includes(key)) continue;

          const transform = pdfjs.Util.transform(viewport.transform, item.transform);
          const fontHeight = Math.hypot(transform[2], transform[3]);

          rects.push({
            left: transform[4],
            top: transform[5] - fontHeight,
            width: item.width * scale,
            height: fontHeight * 1.2,
          });
        }

        setView({
          status: "ready",
          rects,
          size: { width: Math.floor(viewport.width), height: Math.floor(viewport.height) },
          pages: pdf.numPages,
        });
      } catch (error) {
        if (!cancelled && error && error.name !== "RenderingCancelledException") {
          setView((current) => ({ ...current, status: "error" }));
        }
      }
    })();

    return () => {
      cancelled = true;
      if (renderTask) renderTask.cancel();
    };
  }, [docId, pageNumber, source.text, width]);

  useEffect(() => {
    if (view.status !== "ready" || view.rects.length === 0 || !scrollRef.current) return;
    const top = Math.min(...view.rects.map((rect) => rect.top));
    scrollRef.current.scrollTo({ top: Math.max(0, top - 96) });
  }, [view]);

  return (
    <>
      <div aria-hidden="true" onClick={onClose} className="fixed inset-0 z-40 bg-zinc-950/40 xl:hidden" />
      <motion.aside
        aria-label="Source viewer"
        initial={{ opacity: 0, x: 24 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ type: "spring", stiffness: 140, damping: 22 }}
        className="fixed inset-y-0 right-0 z-50 flex w-full max-w-xl flex-col border-l border-zinc-200 bg-zinc-50 shadow-xl xl:static xl:z-auto xl:h-dvh xl:max-w-none xl:shadow-none dark:border-zinc-800 dark:bg-zinc-900"
      >
        <header className="flex items-start justify-between gap-3 border-b border-zinc-200 px-5 py-3 dark:border-zinc-800">
          <div className="min-w-0">
            <h2 className="text-sm font-medium">
              Source {activeIndex + 1} of {sources.length}
            </h2>
            <p className="truncate font-mono text-xs tabular-nums text-zinc-600 dark:text-zinc-400">
              <span translate="no">{filename}</span>, page {pageNumber}
              {view.pages ? ` of ${view.pages}` : ""}
            </p>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label="Close source viewer"
            className="grid size-9 shrink-0 place-items-center rounded-full text-zinc-600 transition hover:bg-zinc-200 active:scale-[0.96] dark:text-zinc-400 dark:hover:bg-zinc-800"
          >
            <X size={18} weight="regular" aria-hidden="true" />
          </button>
        </header>

        <nav aria-label="Sources for this answer" className="flex gap-2 overflow-x-auto border-b border-zinc-200 px-5 py-3 dark:border-zinc-800">
          {sources.map((item, index) => (
            <button
              key={index}
              type="button"
              onClick={() => onSelect(index)}
              aria-pressed={index === activeIndex}
              className={`inline-flex shrink-0 items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition active:scale-[0.98] ${
                index === activeIndex
                  ? "border-emerald-700 bg-emerald-700 text-emerald-50 dark:border-emerald-400 dark:bg-emerald-400 dark:text-emerald-950"
                  : "border-zinc-300 hover:bg-zinc-200/70 dark:border-zinc-700 dark:hover:bg-zinc-800"
              }`}
            >
              <span className="font-mono tabular-nums">{index + 1}</span>
              {typeof item.page === "number" ? `Page ${item.page + 1}` : "Passage"}
            </button>
          ))}
        </nav>

        <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto px-5 py-4 [scrollbar-gutter:stable]">
          <div ref={frameRef} className="w-full">
            <div
              className="relative overflow-hidden rounded-xl border border-zinc-200 dark:border-zinc-700"
              style={view.size ? { width: view.size.width, height: view.size.height } : { minHeight: 320 }}
            >
              <canvas ref={canvasRef} className="block bg-zinc-50 dark:brightness-90" />

              {view.rects.map((rect, index) => (
                <div
                  key={index}
                  aria-hidden="true"
                  className="pointer-events-none absolute rounded-sm bg-emerald-400/40 mix-blend-multiply"
                  style={{ left: rect.left, top: rect.top, width: rect.width, height: rect.height }}
                />
              ))}

              {view.status === "loading" && (
                <div
                  aria-hidden="true"
                  className="absolute inset-0 animate-pulse bg-zinc-200 motion-reduce:animate-none dark:bg-zinc-800"
                />
              )}
            </div>

            {view.status === "error" && (
              <p role="alert" className="mt-3 text-sm text-rose-700 dark:text-rose-300">
                The PDF page could not be loaded. Check that the local server is running and that the original file
                is still in its uploads folder.
              </p>
            )}
          </div>

          <section className="mt-5">
            <h3 className="mb-2 text-sm font-medium">Cited passage</h3>
            <p className="whitespace-pre-wrap wrap-break-word text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
              {source.text}
            </p>
          </section>
        </div>
      </motion.aside>
    </>
  );
}

