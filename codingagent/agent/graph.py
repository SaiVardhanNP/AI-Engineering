from langgraph.graph import StateGraph, START, END
from agent.state import CodingAgentState
from agent.workspace import Workspace
from agent.tools.search import create_search_tools
from agent.tools.filesystem import create_filesystem_tools
from agent.tools.shell import create_shell_tools
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from agent.remote_tool_node import RemoteToolNode
from agent.remote_runtime import RemoteRuntimeClient
import os


load_dotenv()

workspace = Workspace("workspace/sample-project")

runtime = RemoteRuntimeClient("ws://127.0.0.1:8000/ws")

MAX_TEST_ATTEMPTS = 10

remote_tool_node = RemoteToolNode(runtime)

filesystem_tools = create_filesystem_tools(workspace)
search_tools = create_search_tools(workspace)
shell_tools = create_shell_tools(workspace)

tools = filesystem_tools + search_tools + shell_tools

model = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

model_with_tools = model.bind_tools(tools)


def call_model(state: CodingAgentState):
    response = model_with_tools.invoke(state["messages"])

    return {"messages": [response]}


def evaluate_test_result(state: CodingAgentState):
    last_message = state["messages"][-1]

    if last_message.type != "tool":
        return {}
    if last_message.name != "run_command":
        return {}
    content = last_message.content

    if "exit_code: 0" in content:
        return {"task_status": "passed", "test_attempts": state["test_attempts"] + 1}
    return {"task_status": "failed", "test_attempts": state["test_attempts"] + 1}


def route_after_evaluation(state: CodingAgentState):
    if state["task_status"] == "passed":
        return "done"
    if state["test_attempts"] >= MAX_TEST_ATTEMPTS:
        return "max_attempts"

    return "continue"


def route_after_tools(state: CodingAgentState):
    last_message = state["messages"][-1]

    if last_message.type != "tool":
        return "llm"

    if last_message.name == "run_command":
        return "evaluate"

    return "llm"


def should_continue(state: CodingAgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


graph = StateGraph(CodingAgentState)

graph.add_node("llm", call_model)
graph.add_node("tools", remote_tool_node)
graph.add_node("evaluate_test_result", evaluate_test_result)

graph.add_edge(START, "llm")

graph.add_conditional_edges(
    "llm",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

graph.add_conditional_edges(
    "tools",
    route_after_tools,
    {
        "llm": "llm",
        "evaluate": "evaluate_test_result",
    },
)

graph.add_conditional_edges(
    "evaluate_test_result",
    route_after_evaluation,
    {"done": END, "max_attempts": END, "continue": "llm"},
)


app = graph.compile()
