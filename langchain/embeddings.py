from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from keyword_retriever import KeywordRetriever
from retriever import HybridRetriever
from langchain_core.prompts import ChatPromptTemplate
from reranker import CrossEncoderReranker
from mmr import MMR
from dotenv import load_dotenv
from models.answer_model import Answer
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableParallel,
)
import os

load_dotenv()


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


documents = [
    Document(
        page_content="Alan Turing proposed the Turing Test in 1950.",
        metadata={"topic": "turing"},
    ),
    Document(
        page_content="IBM Deep Blue defeated Garry Kasparov in 1997.",
        metadata={"topic": "deep-blue"},
    ),
    Document(
        page_content="IBM Watson defeated human champions on Jeopardy.",
        metadata={"topic": "watson"},
    ),
]


chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI assistant. Answer using only the provided context.",
        ),
        ("human", "Context : {context}\n\n Question: {question}"),
    ]
)


embeddings = GoogleGenerativeAIEmbeddings(
    api_key=os.getenv("GEMINI_API_KEY"), model="gemini-embedding-001"
)

model = ChatGoogleGenerativeAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-3.5-flash-lite",
)

structured_model = model.with_structured_output(Answer)


vector_store = InMemoryVectorStore(embeddings)

vector_store.add_documents(documents)

vector_retriver = vector_store.as_retriever()
keyword_retriver = KeywordRetriever(documents=documents)


reranker = CrossEncoderReranker()

mmr = MMR(
    embeddings=embeddings,
    lambda_mult=0.5,
    top_k=2,
)


retriever = HybridRetriever(
    vector_retriever=vector_retriver,
    keyword_retriever=keyword_retriver,
    reranker=reranker,
    mmr=mmr,
    top_k=2,
)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | chat_prompt_template
    | model
)

results = retriever.invoke("Who defeated Garry Kasparov?")
for doc in results:
    print(doc.page_content)
