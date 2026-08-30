from pathlib import Path
from data_model import Document


def load_documents(directory: str) -> list[Document]:
    documents = []

    directory_path = Path(directory)

    for file_path in directory_path.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        document = Document(id=file_path.stem, text=text)

        documents.append(document)

    return documents
