from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict


class State(TypedDict):
    attempt: int
    evaluation: str


def generate(state: State):
    print("Generation attempt ", state["attempt"])

    return {"attempt": state["attempt"] + 1}


def evaluate(state: State):
    print("Evaluating attempt ", state["attempt"])

    if state["attempt"] < 3:
        return {"evaluation": "bad"}

    return {"evaluation": "good"}


def route(state: State):
    return state["evaluation"]


graph = StateGraph(State)

checkpointer = InMemorySaver()

graph.add_node("generate", generate)
graph.add_node("evaluate", evaluate)


graph.add_edge(START, "generate")

graph.add_edge("generate", "evaluate")


graph.add_conditional_edges("evaluate", route, {"good": END, "bad": "generate"})

app = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "ticket-123"}}


result = app.invoke({"attempt": 0, "evaluation": ""}, config=config)

print(result)
snapshot = app.get_state(config)

print("\n--- Checkpoint ---")
print("Values:", snapshot.values)
print("Next:", snapshot.next)
