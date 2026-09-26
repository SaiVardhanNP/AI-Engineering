from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


document = Document(
    page_content="""
    Alan Turing proposed the Turing Test in 1950.

    IBM Deep Blue defeated Garry Kasparov in 1997.

    IBM Watson later defeated human champions on Jeopardy.
    """,
    metadata={
        "video_id": "history-of-ai",
        "source": "youtube",
    },
)
splitter = RecursiveCharacterTextSplitter(chunk_size=80, chunk_overlap=20)

chunks = splitter.split_documents([document])

for index, chunk in enumerate(chunks, start=1):
    print(f"\n---Chunk {index}---")
    print(chunk)
