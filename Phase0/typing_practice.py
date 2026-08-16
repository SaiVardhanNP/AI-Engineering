from typing import Optional, Literal

name: str = "Vardhan"
age: int = 20
cgpa: float = 9.8
is_student: bool = False


tasks: list[str] = ["Learn AI", "Build a system", "Start a company"]

scores: list[int] = [80, 90, 100]

students: dict[str, str] = [{name: "vardhan"}, {name: "jane"}]


def greet(name: str) -> str:
    return f"Hello {name}"


def average(scores: list[int]) -> float:
    return sum(scores) / len(scores)


def find_task(task_name: str) -> Optional[str]:
    for task in tasks:
        if task.lower() == task_name.lower():
            return task
    return None


def print_value(value: str | int):
    print(value)


def choose_model(model: Literal["GPT-5", "GPT-2", "Claude-Mythos"]):
    print(model)
