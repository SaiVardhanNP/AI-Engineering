from providers.gemini import GeminiProvider
from providers.grok import GroqProvider
from conversation import Conversation
from models.generate_request import ChatRequest
from pipelines.ai_pipeline import AIPipeline


conversation = Conversation()

provider = GeminiProvider()

pipeline = AIPipeline(provider)

while True:
    user_input = input("USER: ")

    conversation.add_user_message(user_input)

    request = ChatRequest(
        messages=conversation.get_messages(),
    )

    response = pipeline.chat(request)

    conversation.add_assistant_message(response)

    print("BOT: " + response)
