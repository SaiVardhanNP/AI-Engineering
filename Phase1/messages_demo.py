messages = [{"role": "system", "content": "You are a Senior AI Engineering Mentor"}]

messages.append({"role": "user", "content": "Hi!"})

messages.append(
    {"role": "assistant", "content": "Hello! What would you like to learn today?"}
)

messages.append({"role": "User", "content": "Teach me about embeddings"})


for message in messages:
    print(f"{message['role'].upper()}:\n {message['content']}")
