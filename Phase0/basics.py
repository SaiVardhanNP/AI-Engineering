tasks = [
    {"title": "Dive into AI", "done": False, "priority": 100},
    {"title": "Get a haircut", "done": True, "priority": 20},
    {"title": "Build an SSE", "done": True, "priority": 30},
    {"title": "Build a WEBRTC", "done": False, "priority": 10},
]


def filter_pending(tasks):
    pending_tasks = []
    for task in tasks:
        if not (task["done"]):
            pending_tasks.append(task)
    return pending_tasks


def summarize(tasks):
    completed, pending = 0, 0

    for task in tasks:
        number = 9
        if task["done"]:
            completed += 1
        else:
            pending += 1
    print(number)
    # Variables are not block scoped in python they are function scoped a loop or an if is just another line of code in python due to which a variable declared inside of an if or for can be accessed out of them within the same function.
    return f"{pending} pending, {completed} done"


tasks_pending = filter_pending(tasks)

status_check = summarize(tasks)

print("Tasks pending: ", tasks_pending)

print(status_check)


tasks_with_titles = [task["title"] for task in tasks]

completed_tasks = [task["title"] for task in tasks if task["done"]]

tasks_with_priority = {task["title"]: task["priority"] for task in tasks}

sorted_tasks = sorted(tasks, key=lambda task: task["priority"], reverse=True)

pending_tasks = sorted(
    [task for task in tasks if not task["done"]],
    key=lambda task: task["priority"],
    reverse=True,
)
print("Tasks with their titles: ", tasks_with_titles)

print("Completed tasks are ", completed_tasks)

print("Tasks with their priorities ", tasks_with_priority)

print("Sorted tasks are: ", sorted_tasks)

print("Pending tasks are: ",pending_tasks)


projects = [
    {
        "name": "AI",
        "tasks": [
            {"title": "Prompting", "done": True},
            {"title": "Embeddings", "done": False},
        ]
    },
    {
        "name": "Backend",
        "tasks": [
            {"title": "Auth", "done": True},
            {"title": "Redis", "done": False},
        ]
    }
]

pending_project_tasks=[
    task['title']
    for project in projects
    for task in project['tasks']
    if not task['done']
]

# for project in projects:
#     for task in project['tasks']:
#         if task['done']:
#             pending_project_tasks.append(task['title'])

print(pending_project_tasks)