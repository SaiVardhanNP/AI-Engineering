import chromadb

client = chromadb.PersistentClient(path="./chroma_db")


collection = client.get_or_create_collection(name="metadatas")

collection.add(
    ids=["doc-001", "doc-002", "doc-003", "doc-004", "doc-005"],
    documents=[
        "Python programming",
        "JavaScript web",
        "Python machine-learning",
        "JavaScript backend",
        "Python web",
    ],
    metadatas=[
        {"language": "Python", "topic": "programming"},
        {"language": "JavaScript", "topic": "web"},
        {"language": "Python", "topic": "machine-learning"},
        {"language": "JavaScript", "topic": "backend"},
        {"language": "Python", "topic": "web"},
    ],
)

lang_results = collection.get(where={"language": "Python"})

topic_results = collection.get(where={"topic": "web"})

and_results = collection.get(where={"$and": [{"language": "Python"}, {"topic": "web"}]})

semantic_result = collection.query(
    query_texts=["programming"], where={"language": "Python"}
)

print(lang_results["documents"])

print(topic_results["documents"])

print(and_results["documents"])

print(semantic_result["documents"])
