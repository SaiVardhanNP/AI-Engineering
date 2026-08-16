class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email


class Task:
    def __init__(self, owner, title, priority, done=False):
        self.title = title
        self.priority = priority
        self.done = done
        self.owner = owner

    def mark_done(self):
        self.done = True

    def increase_priority(self, amount):
        self.priority += amount

    def is_high_priority(self):
        if self.priority > 80:
            return True
        else:
            return False

    def __str__(self):
        return f"Learn {self.title} | Priority: {self.priority} | {'Done' if self.done else 'Pending'}"


class AITask(Task):
    def __init__(
        self,
        owner,
        title,
        priority,
        model,
        done=False,
    ):
        super().__init__(owner, title, priority, done)
        self.model = model

    def run_model(self):
        print("Running ", self.model)


tasks = [
    Task("Learn AI", 90, False),
    Task("Be an FDE", 80, False),
    Task("Be Happy", 100, False),
]

# for task in tasks:
#     match task.title:
#         case "Learn AI":
#             task.increase_priority(10)
#             print("Is highest priority? ", task.is_high_priority())
#         case "Be Happy":
#             task.mark_done()

# for task in tasks:
#     print(task)


owner = User("Vardhan", "vardhan@gmail.com")
ai_task = AITask(owner, "Build GPT", 90, "GTP-5")

print("Task: ",ai_task.title)
print("Owner: ",ai_task.owner.name)
