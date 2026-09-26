import { useRef, useState } from "react";
import { motion, useMotionValueEvent, useScroll } from "motion/react";
import Reveal from "./Reveal.jsx";
import Shot from "./Shot.jsx";

const STEPS = [
  {
    title: "Add a PDF",
    body: "Drop a file in. Folio splits it into passages and indexes them on your machine.",
    shot: "empty",
    alt: "Folio with a document selected and suggested questions to start with",
  },
  {
    title: "Ask in Plain Language",
    body: "Vector search and keyword search run together, so meaning and exact terms both count.",
    shot: "answer",
    alt: "An answer with numbered citation chips and a row of source pages underneath",
  },
  {
    title: "Check the Source",
    body: "Every answer links to the passages it used. Click one and the PDF page opens with the lines highlighted.",
    shot: "split",
    alt: "The PDF page beside the chat, with the cited passage highlighted in green",
  },
  {
    title: "Pick the Model",
    body: "Switch between local Gemma, Gemini and Groq models in the middle of a conversation.",
    shot: "menu",
    alt: "The model menu open, listing local, Gemini and Groq models",
  },
];

function StepText({ step, active }) {
  return (
    <div className={`transition-opacity duration-300 ${active ? "opacity-100" : "opacity-60"}`}>
      <h3 className="text-xl font-semibold tracking-tight">{step.title}</h3>
      <p className="mt-2 max-w-[44ch] text-base leading-relaxed text-zinc-600 dark:text-zinc-400">{step.body}</p>
    </div>
  );
}

function Frame({ children }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-zinc-200 shadow-[0_30px_70px_-40px_rgba(4,120,87,0.4)] dark:border-zinc-800 dark:shadow-black/60">
      {children}
    </div>
  );
}

export default function Story() {
  const track = useRef(null);
  const [active, setActive] = useState(0);

  const { scrollYProgress } = useScroll({ target: track, offset: ["start start", "end end"] });

  useMotionValueEvent(scrollYProgress, "change", (value) => {
    setActive(Math.max(0, Math.min(STEPS.length - 1, Math.floor(value * STEPS.length))));
  });

  return (
    <section id="how" className="scroll-mt-16">
      <div className="mx-auto max-w-7xl px-5 pt-24 md:px-8 lg:pb-0">
        <Reveal>
          <h2 className="max-w-[18ch] text-4xl font-semibold leading-tight tracking-tight text-balance md:text-5xl">
            From Upload to Cited Answer
          </h2>
        </Reveal>
      </div>

      <div ref={track} className="relative hidden lg:block" style={{ height: `${STEPS.length * 85}vh` }}>
        <div className="sticky top-16 mx-auto grid h-[calc(100dvh-4rem)] max-w-7xl grid-cols-[minmax(0,4fr)_minmax(0,7fr)] items-center gap-14 px-8">
          <div className="relative flex flex-col gap-10 pl-7">
            <div className="absolute inset-y-1 left-0 w-0.5 rounded-full bg-zinc-200 dark:bg-zinc-800">
              <motion.div
                style={{ scaleY: scrollYProgress }}
                className="h-full origin-top rounded-full bg-emerald-700 dark:bg-emerald-400"
              />
            </div>
            {STEPS.map((step, index) => (
              <StepText key={step.title} step={step} active={index === active} />
            ))}
          </div>

          <Frame>
            <div className="relative aspect-[8/5]">
              {STEPS.map((step, index) => (
                <motion.div
                  key={step.shot}
                  className="absolute inset-0"
                  animate={{ opacity: index === active ? 1 : 0, scale: index === active ? 1 : 0.985 }}
                  transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
                >
                  <Shot name={step.shot} alt={step.alt} className="block h-full w-full object-cover" />
                </motion.div>
              ))}
            </div>
          </Frame>
        </div>
      </div>

      <div className="mx-auto mt-12 flex max-w-7xl flex-col gap-16 px-5 pb-8 md:px-8 lg:hidden">
        {STEPS.map((step) => (
          <Reveal key={step.title} className="flex flex-col gap-5">
            <StepText step={step} active />
            <Frame>
              <Shot name={step.shot} alt={step.alt} className="block h-auto w-full" />
            </Frame>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
