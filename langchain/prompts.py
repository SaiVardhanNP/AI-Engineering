from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from models.answer_model import Answer

load_dotenv()

parser = StrOutputParser()

model = ChatGoogleGenerativeAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-3.5-flash-lite",
)

structured_model = model.with_structured_output(Answer)

prompt_template = PromptTemplate.from_template(
    "Answer the following question using this context\n\n"
    "Context: {context}\n\n"
    "Question: {question}"
)

chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI assistant. Answer using only the provided context.",
        ),
        ("human", "Context : {context}\n\n Question: {question}"),
    ]
)

prompt_tempate_result = prompt_template.invoke(
    {
        "context": "Alan Turing proposed the Turing Test in 1950.",
        "question": "Who proposed the turing test?",
    },
)

chain = chat_prompt_template | structured_model

result = chain.invoke(
    {
        "context": "Alan Turing proposed the Turing Test in 1950.",
        "question": "Who proposed the Turing Test?",
    }
)

print("RESULT:", result)
print("TYPE:", type(result))
