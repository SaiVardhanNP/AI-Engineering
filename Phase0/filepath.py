from pathlib import Path

PROJECT = Path("AI_Project")
DATA = PROJECT / "data"
PROMPTS = DATA / "prompts"

prompt = PROMPTS / "summarize.txt"

print(prompt)

print(prompt.parent)
print(prompt.name)
print(prompt.suffix)
