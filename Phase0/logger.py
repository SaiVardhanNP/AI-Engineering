import logging
from dataclasses import dataclass


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)



@dataclass
class Task:
    title: str
    priority: int
    done: bool = False

    def mark_done(self):
        self.done = True
        logging.info(f"Task Completed {self.title}")

    def increase_priority(self, amount):
        self.priority = self.priority + amount
        if self.priority<0:
            raise ValueError("Priority cannot be negative")

    def is_high_priority(self):
        return self.priority > 80
    
    def __post_init__(self):
        logging.info("Created task: %s", self.title)

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


try:
    task = AITask(title="Build Claude", priority=80,model_name="GPT-5")
    task.increase_priority(-40)

except ValueError as e:
    logging.exception(e)

message = ChatMessage(
    "Build an agent", "Understand the requirement and build build an agent", 100
)

print(message.cost())

print(task.is_high_priority())

task.increase_priority(30)

task.mark_done()

print(task)
