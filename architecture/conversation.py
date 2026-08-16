class Conversation:
    def __init__(self):
        self.messages = []

    def add_user_message(self, text):
        self.messages.append({"role": "user", "content": text})

    def add_assistant_message(self, text):
        self.messages.append({"role": "assistant", "content": text})

    def get_messages(self):
        return self.messages
