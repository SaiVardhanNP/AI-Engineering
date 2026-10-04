import {
  Check,
  ChatText,
  CircleNotch,
  Compass,
  Receipt,
  ShieldCheck,
  UserCircle,
  Wrench,
  X,
} from "@phosphor-icons/react";
import { motion, useReducedMotion } from "motion/react";

// Everything is laid out on one 412 x 232 grid. Nodes are HTML (so they can hold
// real icons) and edges are an SVG underlay that uses the same coordinates.
const W = 412;
const H = 232;
const NODE_W = 76;
const NODE_H = 44;

const NODES = {
  router: { x: 0, y: 94, label: "Router", Icon: Compass },
  billing: { x: 112, y: 12, label: "Billing", Icon: Receipt },
  account: { x: 112, y: 94, label: "Account", Icon: UserCircle },
  technical: { x: 112, y: 176, label: "Technical", Icon: Wrench },
  responder: { x: 224, y: 94, label: "Responder", Icon: ChatText },
  evaluator: { x: 336, y: 94, label: "Evaluator", Icon: ShieldCheck },
};

const EDGES = [
  ["router", "billing"],
  ["router", "account"],
  ["router", "technical"],
  ["billing", "responder"],
  ["account", "responder"],
  ["technical", "responder"],
  ["responder", "evaluator"],
];

const NODE_STYLE = {
  idle: "border-ink-700 bg-ink-900 text-ink-500",
  queued: "border-dashed border-ink-500 bg-ink-900 text-ink-300",
  working: "border-signal bg-ink-800 text-signal shadow-[0_0_24px_-8px_var(--color-signal)]",
  done: "border-signal-dim bg-ink-900 text-signal",
  failed: "border-alert bg-ink-900 text-alert",
};

const STATE_LABEL = {
  idle: "idle",
  queued: "waiting",
  working: "working",
  done: "done",
  failed: "failed",
};

function edgePath(from, to) {
  const x1 = NODES[from].x + NODE_W;
  const y1 = NODES[from].y + NODE_H / 2;
  const x2 = NODES[to].x;
  const y2 = NODES[to].y + NODE_H / 2;
  return `M ${x1} ${y1} C ${x1 + 20} ${y1}, ${x2 - 20} ${y2}, ${x2} ${y2}`;
}

// flow: the source is producing work for the target. done: both finished.
function edgeState(agents, from, to) {
  if (agents[from] === "done" && agents[to] === "done") return "done";
  if (agents[from] === "working" || (agents[from] === "done" && agents[to] === "working")) return "flow";
  return "idle";
}

function Edge({ from, to, state, reduce }) {
  const common = { d: edgePath(from, to), fill: "none", strokeWidth: 1.5, strokeLinecap: "round" };

  if (state === "flow") {
    return (
      <motion.path
        {...common}
        stroke="var(--color-signal)"
        strokeDasharray="4 6"
        animate={reduce ? undefined : { strokeDashoffset: [0, -20] }}
        transition={{ duration: 0.9, repeat: Infinity, ease: "linear" }}
      />
    );
  }

  return <path {...common} stroke={state === "done" ? "var(--color-signal-dim)" : "var(--color-ink-700)"} />;
}

function StateGlyph({ state }) {
  if (state === "working") return <CircleNotch size={12} weight="bold" className="animate-spin" aria-hidden />;
  if (state === "done") return <Check size={12} weight="bold" aria-hidden />;
  if (state === "failed") return <X size={12} weight="bold" aria-hidden />;
  return null;
}

function Node({ id, state }) {
  const { x, y, label, Icon } = NODES[id];

  return (
    <div
      className={`absolute flex flex-col items-center justify-center gap-0.5 rounded-xl border transition-colors duration-300 ${NODE_STYLE[state]}`}
      style={{
        left: `${(x / W) * 100}%`,
        top: `${(y / H) * 100}%`,
        width: `${(NODE_W / W) * 100}%`,
        height: `${(NODE_H / H) * 100}%`,
      }}
      title={`${label}: ${STATE_LABEL[state]}`}
    >
      <Icon size={16} weight="regular" aria-hidden />
      <span className="font-mono text-[10px] leading-none">{label}</span>
      <span className="absolute right-1 top-1">
        <StateGlyph state={state} />
      </span>
    </div>
  );
}

export default function CrewMap({ agents }) {
  const reduce = useReducedMotion();

  const summary = Object.entries(NODES)
    .map(([id, node]) => `${node.label} ${STATE_LABEL[agents[id]]}`)
    .join(", ");

  return (
    <div
      className="relative w-full"
      style={{ aspectRatio: `${W} / ${H}` }}
      role="img"
      aria-label={`Agent crew status: ${summary}`}
    >
      <svg viewBox={`0 0 ${W} ${H}`} className="absolute inset-0 h-full w-full" aria-hidden>
        {EDGES.map(([from, to]) => (
          <Edge key={`${from}-${to}`} from={from} to={to} state={edgeState(agents, from, to)} reduce={reduce} />
        ))}
      </svg>
      {Object.keys(NODES).map((id) => (
        <Node key={id} id={id} state={agents[id]} />
      ))}
    </div>
  );
}
