messages = [{"role": "system", "content": "You are an AI Engineering mentor."}]

messages.extend(
    [
        {"role": "user", "content": "Hi!"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "Explain embeddings."},
        {"role": "assistant", "content": "Embeddings convert data into vectors"},
        {"role": "user", "content": "Can you give a real-world analogy?"},
    ]
)


print("Current Conversation")

for message in messages:
    print(f"{message['role'].upper()}:\n {message['content']}\n")
    
print(f"\nTotal messages being sent: {len(messages)}")