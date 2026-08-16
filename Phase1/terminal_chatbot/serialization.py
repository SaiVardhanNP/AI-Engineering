messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi!"},
    {"role": "user", "content": "Explain Python lists."},
]


def to_chatml(messages:list)->str:
    lines=[]
    
    for message in messages:
        lines.append(f"<|{message['role']}|>")
        lines.append(f"{message['content']}\n")
    return "\n".join(lines)

result = to_chatml(messages)

print(result)
