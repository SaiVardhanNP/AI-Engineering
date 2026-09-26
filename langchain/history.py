from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()


model = ChatGoogleGenerativeAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-3.5-flash-lite",
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("placeholder", "{history}"),
        ("human", "{input}"),
    ]
)

chain = prompt | model

store = {}


def get_session_history(session_id: str):

    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()

    return store[session_id]


conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


response = conversation.invoke(
    {"input": "My name is Vardhan."}, config={"configurable": {"session_id": "user-1"}}
)

print(response.content)

response = conversation.invoke(
    {"input": "What is my name?"}, config={"configurable": {"session_id": "user-1"}}
)

print(response.content)
