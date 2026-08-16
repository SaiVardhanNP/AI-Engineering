from Phase1.terminal_chatbot.prompts.prompt import SYSTEM_PROMPT

messages = [{"role": "system", "content": SYSTEM_PROMPT}]


def add_user_message(prompt: str):
    messages.append({"role": "user", "content": prompt})


def add_assistant_message(respose: str):
    messages.append({"role": "assistant", "content": respose})


def trim_history(limit: int):
    system_prompt = next((msg for msg in messages if msg["role"] == "system"), None)

    trimmed_messages = [msg for msg in messages if msg["role"] != "system"]

    messages[:] = [system_prompt] + trimmed_messages[-limit:]
