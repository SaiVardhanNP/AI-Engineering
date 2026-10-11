from typing import Annotated, TypedDict
import operator
from langgraph.graph import StateGraph, START, END


class SupportState(TypedDict):
    ticket: str
    findings: Annotated[list[str], operator.add]


def coordinator(state: SupportState):
    print("Coordinator started")

    return {}


def billing_check(state: SupportState):
    print("Billing check started")

    return {"findings": ["Payment succeeded"]}


def technical_check(state: SupportState):
    print("Technical check started")

    return {"findings": ["Application crashed"]}


def account_check(state: SupportState):
    return {"findings": ["Account is active"]}


graph = StateGraph(SupportState)

graph.add_node("coordinator", coordinator)
graph.add_node("billing", billing_check)
graph.add_node("technical", technical_check)
graph.add_node("account", account_check)

graph.add_edge(START, "coordinator")

graph.add_edge("coordinator", "billing")
graph.add_edge("coordinator", "technical")
graph.add_edge("coordinator", "account")
graph.add_edge("billing", END)
graph.add_edge("technical", END)
graph.add_edge("account", END)


app = graph.compile()

result = app.invoke(
    {"ticket": "My payment succeeded but the application crashed", "findings": []}
)

print(result)
