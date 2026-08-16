from dataclasses import dataclass


@dataclass
class Task:
    title: str
    priority: int
    done: bool = False

    def mark_done(self):
        self.done = True

    def increase_priority(self, amount):
        self.priority = max(0, self.priority + amount)

    def is_high_priority(self):
        return self.priority > 80

@dataclass
class AITask(Task):
    model_name:str="GPT-2"
    
    def describe(self):
        print(self.model_name)

@dataclass
class ChatMessage:
    role: str
    content: str
    tokens: int

    def cost(self):
        return self.tokens * 0.00001


task = AITask(title="Build Claude", priority=80,model_name="GPT-5")

message = ChatMessage(
    "Build an agent", "Understand the requirement and build build an agent", 100
)

print(message.cost())

print(task.is_high_priority())

task.increase_priority(30)

task.mark_done()

print(task)
