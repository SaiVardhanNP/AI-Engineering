role_map = {"user": "user", "assistant": "model"}


def to_gemini(messages: list) -> dict:
    return {
        "system_prompt": next(
            msg["content"] for msg in messages if msg["role"] == "system"
        ),
        "messages": [
            {"role": role_map[msg["role"]], "parts": [{"text": msg["content"]}]}
            for msg in messages
            if msg["role"] != "system"
        ],
    }
