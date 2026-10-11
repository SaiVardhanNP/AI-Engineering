from langgraph.graph import StateGraph, START, END
from pymongo import MongoClient
from typing import TypedDict, Literal
from langgraph.types import interrupt, Command
from langgraph.checkpoint.mongodb import MongoDBSaver


client = MongoClient(
    "mongodb+srv://saivardhannp:saivardhan11@mydatabase.vzet070.mongodb.net/"
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


# The graph must be built exactly like in langgraph_mongo.py so the saved
# checkpoint lines up with the same nodes.
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


# Same thread_id as the paused run -> loads its checkpoint from MongoDB.
config = {"configurable": {"thread_id": "support-123"}}


# Check the run is actually paused at human_review.
snapshot = app.get_state(config)

print("Saved state:", snapshot.values)
print("Next node:", snapshot.next)

if not snapshot.next:
    print("Nothing to resume: this thread has no pending interrupt.")
else:
    # Resume with the human's decision. This value becomes the return
    # value of interrupt() inside human_review.
    # Use "approved" to send the response, or "reject" to end the run.
    result = app.invoke(Command(resume="approved"), config=config)

    print(result)
    print(app.get_state(config).values)
    print(app.get_state(config).next)  # () once the graph has finished
