from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Literal


class State(TypedDict):
    message: str
    decision: Literal["approved", "reject"]


def generate(state: State):
    print("Generating response...")

    return {"message": "Your request has been processed"}


def human_review(state: State):

    print("Waiting for human review")

    decision = interrupt("Approve this response?")

    return {"decision": decision}


def route_review(state: State):

    return state["decision"]


def send_response(state: State):
    print("Sending response...")

    return {}


graph = StateGraph(State)

graph.add_node("generate", generate)
graph.add_node("human_review", human_review)
graph.add_node("send_response", send_response)


graph.add_edge(START, "generate")
graph.add_edge("generate", "human_review")
graph.add_conditional_edges(
    "human_review", route_review, {"approved": "send_response", "reject": END}
)
graph.add_edge("send_response", END)

checkpointer = InMemorySaver()

app = graph.compile(checkpointer=checkpointer)


config_1 = {"configurable": {"thread_id": "support-123"}}

config_2 = {"configurable": {"thread_id": "support_456"}}

result_1 = app.invoke({"message": "", "decision": ""}, config=config_1)

print(result_1)

snapshot = app.get_state(config=config_1)

print("Values", snapshot.values)
print("Next:", snapshot.next)


result = app.invoke(Command(resume="reject"), config=config_1)

print("\n--- Resumed ---")

print(result)


result_2 = app.invoke({"message": "", "decision": ""}, config=config_2)


print(result_2)

snapshot = app.get_state(config=config_2)

print("Values", snapshot.values)
print("Next:", snapshot.next)


result = app.invoke(Command(resume="approved"), config=config_2)

print("\n--- Resumed ---")

print(result)
