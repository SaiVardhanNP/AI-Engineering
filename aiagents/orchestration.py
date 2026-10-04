from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()


class TaskResponse(BaseModel):
    worker: Literal["billing", "technical", "account"] = Field(
        description="describes the type of worked needed"
    )
    task_detail: str = Field(description="Describe the task in a detailed manner")
    depends_on: list[str] = Field(
        default_factory=list,
        description="Workers that must complete before this worker can start",
    )


class OrchestratorResponse(BaseModel):
    tasks: list[TaskResponse]


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def billing_worker(task: str):
    return f"Billing worker investigated: {task}"


def technical_worker(task: str):
    return f"Technical worker investigated: {task}"


def account_worker(task: str):
    return f"Account worker investigated: {task}"


workers = {
    "billing": billing_worker,
    "technical": technical_worker,
    "account": account_worker,
}


def orchestrator(ticket: str) -> OrchestratorResponse:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=ticket,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", response_schema=OrchestratorResponse
        ),
    )
    return response.parsed


ticket = "My subscription shows inactive even though I was charged."


plan = orchestrator(ticket)

task_results = []

completed_workers = {}
pending_tasks = plan.tasks.copy()

while pending_tasks:
    progress = False

    for task in pending_tasks.copy():
        dependencies_ready = all(
            dependency in completed_workers for dependency in task.depends_on
        )

        if not dependencies_ready:
            continue

        worker_result = workers[task.worker](task.task_detail)

        completed_workers[task.worker] = worker_result

        pending_tasks.remove(task)

        progress = True

    if not progress:
        raise RuntimeError(
            "Unable to make progress. There may be a circular or invalid dependency."
        )
print(completed_workers)