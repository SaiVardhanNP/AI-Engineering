from langgraph.graph import StateGraph, START, END
from pymongo import MongoClient
from typing import TypedDict, Literal
from langgraph.types import interrupt
from langgraph.checkpoint.mongodb import MongoDBSaver
import os

client = MongoClient(
    ""
)

checkpointer = MongoDBSaver(client, db_name="langgraph")


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




app = graph.compile(checkpointer=checkpointer)


config = {"configurable": {"thread_id": "support-123"}}


result = app.invoke({"message": "", "decision": ""}, config=config)

print(result)


snapshot = app.get_state(config)

print(snapshot.values)
print(snapshot.next)
