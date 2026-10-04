// Pure functions that turn the backend's stream events into UI state for one run.
// No React in here, so the logic can be tested on its own.

export const AGENT_KEYS = ["router", "billing", "account", "technical", "responder", "evaluator"];
const DOMAINS = ["billing", "account", "technical"];

// Agent states: idle, queued (will be needed), working, done, failed.
export function initialRun(now = Date.now()) {
  return {
    status: "running", // running | done | escalated | error
    startedAt: now,
    elapsed: null,
    steps: [],
    agents: Object.fromEntries(AGENT_KEYS.map((key) => [key, "idle"])),
    categories: [],
    reply: null,
    ticketId: null,
    conversationId: null,
    needsHuman: false,
    error: null,
  };
}

const closeStageSteps = (steps, status = "done") =>
  steps.map((step) => (step.kind === "stage" && step.status === "running" ? { ...step, status } : step));

const closeAllSteps = (steps, status) =>
  steps.map((step) => (step.status === "running" ? { ...step, status } : step));

const setAgents = (agents, keys, state, onlyFrom) =>
  Object.fromEntries(
    Object.entries(agents).map(([key, current]) => [
      key,
      keys.includes(key) && (!onlyFrom || onlyFrom.includes(current)) ? state : current,
    ]),
  );

function addStep(steps, step) {
  return [...steps, { id: steps.length, ...step }];
}

function applyStage(run, ev) {
  const steps = closeStageSteps(run.steps);
  const stageStep = (status) => addStep(steps, { kind: "stage", label: ev.label, status, t: ev.t });
  const active = run.categories;

  switch (ev.stage) {
    case "started":
      return { ...run, steps: stageStep("done") };

    case "classifying":
      return { ...run, steps: stageStep("running"), agents: setAgents(run.agents, ["router"], "working") };

    case "classified": {
      const categories = (ev.categories ?? []).filter((c) => DOMAINS.includes(c));
      return {
        ...run,
        steps: stageStep("done"),
        categories,
        agents: setAgents(
          setAgents(run.agents, ["router"], "done"),
          categories.length > 0 ? [...categories, "responder", "evaluator"] : [],
          "queued",
          ["idle"],
        ),
      };
    }

    case "investigating":
      return {
        ...run,
        steps: stageStep("running"),
        agents: setAgents(run.agents, active, "working", ["idle", "queued"]),
      };

    case "checking":
      // the domain agents and the responder have finished by the time checking starts
      return {
        ...run,
        steps: stageStep("running"),
        agents: setAgents(setAgents(run.agents, [...active, "responder"], "done"), ["evaluator"], "working"),
      };

    case "revising":
      return {
        ...run,
        steps: stageStep("running"),
        agents: setAgents(setAgents(run.agents, ["responder"], "working"), ["evaluator"], "queued"),
      };

    default:
      return { ...run, steps: stageStep("done") };
  }
}

export function applyEvent(run, ev) {
  switch (ev.type) {
    case "stage":
      return applyStage(run, ev);

    case "tool_start":
      return {
        ...run,
        steps: addStep(run.steps, { kind: "tool", agent: ev.agent, tool: ev.tool, label: ev.label, status: "running", t: ev.t }),
        agents: setAgents(run.agents, [ev.agent], "working"),
      };

    case "tool_end": {
      // close the most recent matching step that is still running
      let index = -1;
      run.steps.forEach((step, i) => {
        if (step.kind === "tool" && step.agent === ev.agent && step.tool === ev.tool && step.status === "running") index = i;
      });
      if (index === -1) return run;

      return {
        ...run,
        steps: run.steps.map((step, i) => (i === index ? { ...step, status: ev.ok === false ? "failed" : "done" } : step)),
      };
    }

    case "done": {
      // a greeting or out-of-scope ticket never reaches the responder or evaluator
      const finished = run.categories.length > 0 ? [...run.categories, "router", "responder", "evaluator"] : ["router"];
      return {
        ...run,
        status: ev.status === "escalated" ? "escalated" : "done",
        steps: closeAllSteps(run.steps, "done"),
        agents: setAgents(run.agents, finished, "done", ["idle", "queued", "working"]),
        reply: ev.reply,
        ticketId: ev.ticket_id ?? null,
        conversationId: ev.conversation_id ?? null,
        needsHuman: Boolean(ev.needs_human),
        elapsed: ev.t,
      };
    }

    case "error":
      return {
        ...run,
        status: "error",
        steps: closeAllSteps(run.steps, "failed"),
        agents: setAgents(run.agents, AGENT_KEYS, "failed", ["working"]),
        error: ev.message,
        elapsed: ev.t ?? (Date.now() - run.startedAt) / 1000,
      };

    default:
      return run;
  }
}
