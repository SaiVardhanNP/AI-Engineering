import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="documents")

collection.add(
    ids=["doc-001", "doc-002", "doc-003"],
    documents=[
        "Python is a programming language.",
        "JavaScript runs in browsers and servers.",
        "NumPy provides numerical computing capabilities.",
    ],
)

record = collection.get(ids=["doc-002"])

print("Record with id doc-2 is ", record["documents"][0])

collection.update(
    ids=["doc-002"],
    documents=["Python is now a days most popularily being used in AI."],
)

updated_record = collection.get(ids=["doc-002"])

print(updated_record["documents"][0])


collection.delete(ids=["doc-003"])

collection.upsert(ids=["doc-003"], documents=["Python is running the AI Industry."])


print(collection.get())
