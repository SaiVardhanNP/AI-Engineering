import queue
import time

from crewai.events import (
    ToolUsageFinishedEvent,
    ToolUsageStartedEvent,
    crewai_event_bus,
)

# keyed by the tool's function name, which is what CrewAI reports in events
TOOL_LABELS = {
    "get_payment_details": "Checking your payments",
    "get_invoice": "Looking up your invoice",
    "get_subscription_billing": "Checking billing for your subscription",
    "get_account_status": "Checking your account",
    "get_subscription_status": "Checking your subscription status",
    "get_error_logs": "Reading your recent error logs",
    "search_known_issues": "Searching known issues",
    "search_support_docs": "Searching the documentation",
}

KEEPALIVE_SECONDS = 15


class ActivityStream:
    """Collects what the pipeline is doing for ONE request, as a stream of events.

    Pipeline stages call emit() directly. Tool calls inside the agents are picked
    up from CrewAI's event bus. The bus is global, so events are matched to this
    request by agent id: agents are built per request, so no other request's
    events can leak in.
    """

    def __init__(self):
        self._queue = queue.Queue()
        self._started = time.time()
        self._agent_keys = {}
        self._handlers = []

    def emit(self, event_type, **data):
        self._queue.put({"type": event_type, "t": round(time.time() - self._started, 1), **data})

    def watch(self, agents):
        """Start reporting tool calls made by these agents ({key: Agent})."""
        self._agent_keys = {str(agent.id): key for key, agent in agents.items()}

        def on_tool_start(source, event):
            key = self._agent_keys.get(str(event.agent_id))
            if key:
                self.emit(
                    "tool_start",
                    agent=key,
                    tool=event.tool_name,
                    label=TOOL_LABELS.get(event.tool_name, event.tool_name),
                )

        def on_tool_end(source, event):
            key = self._agent_keys.get(str(event.agent_id))
            if key:
                self.emit(
                    "tool_end",
                    agent=key,
                    tool=event.tool_name,
                    label=TOOL_LABELS.get(event.tool_name, event.tool_name),
                    ok=not event.failure,
                )

        for event_class, handler in (
            (ToolUsageStartedEvent, on_tool_start),
            (ToolUsageFinishedEvent, on_tool_end),
        ):
            crewai_event_bus.register_handler(event_class, handler)
            self._handlers.append((event_class, handler))

    def close(self):
        # let handlers that are still running deliver their events first
        try:
            crewai_event_bus.flush()
        except Exception:
            pass

        for event_class, handler in self._handlers:
            crewai_event_bus.off(event_class, handler)
        self._handlers = []

        self._queue.put(None)

    def events(self):
        """Yield events until close(). Yields None as a keepalive when idle."""
        while True:
            try:
                event = self._queue.get(timeout=KEEPALIVE_SECONDS)
            except queue.Empty:
                yield None
                continue

            if event is None:
                return

            yield event
