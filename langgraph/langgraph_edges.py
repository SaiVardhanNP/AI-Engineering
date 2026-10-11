from langgraph.graph import START, END, StateGraph
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


class ClassificationResponse(BaseModel):
    category: Literal["billing", "technical", "account"] = Field(
        description="describes the class in which the ticket fits."
    )


class SupportState(TypedDict):
    ticket: str
    category: str
    response: str


client = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite", api_key=os.getenv("GEMINI_API_KEY")
)

structured_model = client.with_structured_output(ClassificationResponse)

prompt = ChatPromptTemplate.from_template(
    "Classify this support ticket as billing, technical or account: {ticket}"
)

chain = prompt | structured_model


def classify_ticket(state: SupportState):
    result = chain.invoke({"ticket": state["ticket"]})
    return {"category": result.category}


def billing_handler(state: SupportState):
    return {"response": "We'll check your charges and get back to you."}


def account_handler(state: SupportState):
    return {"response": "We'll help you get back into your account."}


def technical_handler(state: SupportState):
    return {"response": "Our engineers will look into this."}


def route_ticket(state: SupportState):
    return state["category"]


graph = StateGraph(SupportState)

graph.add_node("classifier", classify_ticket)

graph.add_node("billing", billing_handler)
graph.add_node("account", account_handler)
graph.add_node("technical", technical_handler)


graph.add_edge(START, "classifier")

graph.add_conditional_edges(
    "classifier",
    route_ticket,
    {"billing": "billing", "account": "account", "technical": "technical"},
)

graph.add_edge("billing", END)
graph.add_edge("account", END)
graph.add_edge("technical", END)

app = graph.compile()

state = {
    "ticket": "The application is crashing",
    "category": "",
    "response": "",
}
result = app.invoke(state)

print(result)
