messages = [
    {"role": "system", "content": "You are an AI Engineering mentor."},
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello! How can I help you today?"},
    {"role": "user", "content": "What are embeddings?"},
    {
        "role": "assistant",
        "content": "Embeddings convert text or other data into numerical vectors that capture semantic meaning.",
    },
    {"role": "user", "content": "Why are they useful?"},
    {
        "role": "assistant",
        "content": "They allow applications to compare semantic similarity, perform search, clustering, and retrieval.",
    },
    {"role": "user", "content": "What is a token?"},
    {
        "role": "assistant",
        "content": "A token is a chunk of text that an LLM processes, such as a word, part of a word, or punctuation.",
    },
    {"role": "user", "content": "Can LLMs access databases directly?"},
    {
        "role": "assistant",
        "content": "No. They generate text, while your application queries the database and provides the retrieved data to the model.",
    },
]

print(len(messages))


def get_recent_messages(messages: list, limit: int) -> list:

    system_message = next(msg for msg in messages if msg["role"] == "system")
    
    conversation= [msg for msg in messages if msg['role']!='system']
    return [system_message] + conversation[-limit:]


extracted_msgs = get_recent_messages(messages, 100)

print("Original messages count: ", len(messages))

print("Returned messages count:", len(extracted_msgs))

for msg in extracted_msgs:
    print(msg)
