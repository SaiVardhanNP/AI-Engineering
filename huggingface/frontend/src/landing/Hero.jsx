import { useRef } from "react";
import { Link } from "react-router-dom";
import { motion, useReducedMotion, useScroll, useTransform } from "motion/react";
import { ArrowRight } from "@phosphor-icons/react";
import Shot from "./Shot.jsx";

const ease = [0.16, 1, 0.3, 1];

function HeadlineLine({ children, delay, accent = false }) {
  return (
    <span className="block overflow-hidden pb-2">
      <motion.span
        className={`block ${accent ? "text-emerald-700 dark:text-emerald-400" : ""}`}
        initial={{ y: "110%" }}
        animate={{ y: 0 }}
        transition={{ duration: 0.8, ease, delay }}
      >
        {children}
      </motion.span>
    </span>
  );
}

export default function Hero() {
  const ref = useRef(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] });
  const shift = useTransform(scrollYProgress, [0, 1], [0, -70]);

  return (
    <section ref={ref} className="overflow-hidden">
      <div className="mx-auto grid max-w-7xl items-center gap-12 px-5 pb-16 pt-12 md:px-8 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] lg:pb-20 lg:pt-20">
        <div>
          <h1 className="text-5xl font-semibold leading-[1.02] tracking-tighter md:text-6xl">
            <HeadlineLine delay={0}>Ask Your PDFs.</HeadlineLine>
            <HeadlineLine delay={0.12} accent>
              See the Page.
            </HeadlineLine>
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease, delay: 0.35 }}
            className="mt-6 max-w-[46ch] text-lg leading-relaxed text-zinc-600 dark:text-zinc-400"
          >
            Folio answers from your documents, shows the exact passage on the page, and lets you choose which model
            thinks.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease, delay: 0.5 }}
            className="mt-9 flex flex-wrap items-center gap-3"
          >
            <Link
              to="/app"
              className="inline-flex items-center gap-2 rounded-full bg-emerald-700 px-6 py-3 text-base font-medium text-emerald-50 transition hover:bg-emerald-800 active:scale-[0.98] dark:bg-emerald-400 dark:text-emerald-950 dark:hover:bg-emerald-300"
            >
              Open Folio
              <ArrowRight size={18} weight="regular" aria-hidden="true" />
            </Link>
            <a
              href="#how"
              className="inline-flex items-center rounded-full border border-zinc-300 px-6 py-3 text-base font-medium transition hover:bg-zinc-200/70 active:scale-[0.98] dark:border-zinc-700 dark:hover:bg-zinc-800"
            >
              See How It Works
            </a>
          </motion.div>
        </div>

        <motion.div style={{ y: reduce ? 0 : shift }} className="relative lg:-mr-[12vw]">
          <motion.div
            initial={{ opacity: 0, y: 32, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.9, ease, delay: 0.25 }}
            className="overflow-hidden rounded-2xl border border-zinc-200 shadow-[0_40px_90px_-40px_rgba(4,120,87,0.45)] dark:border-zinc-800 dark:shadow-black/60"
          >
            <Shot
              name="split"
              alt="Folio showing an answer with numbered citations on the left and the cited PDF page with the passage highlighted on the right"
              priority
              className="block h-auto w-full max-lg:aspect-[5/4] max-lg:object-cover max-lg:object-[62%_50%]"
            />
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
