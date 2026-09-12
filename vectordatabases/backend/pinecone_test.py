import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "ai-engineering-demo"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=3,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(index_name)

index.upsert(
    vectors=[
        {
            "id": "doc-001",
            "values": [0.1, 0.2, 0.3],
            "metadata": {
                "text": "Python is a programming language.",
                "topic": "programming",
                "language": "Python",
            },
        },
        {
            "id": "doc-002",
            "values": [0.8, 0.7, 0.9],
            "metadata": {
                "text": "JavaScript is used for web development.",
                "topic": "web",
                "language": "Javascript",
            },
        },
        {
            "id": "doc-003",
            "values": [0.2, 0.1, 0.4],
            "metadata": {
                "text": "NumPy is used for numerical computing.",
                "topic": "python",
                "language": "Python",
            },
        },
    ]
)

# print(index.describe_index_stats())

query_vector = [0.8, 0.7, 0.85]

results = index.query(vector=query_vector, top_k=3, include_metadata=True)

# print(results)


query_result = index.query(
    vector=query_vector,
    filter={"language": {"$eq": "Python"}},
    include_metadata=True,
    top_k=3,
)

# print(query_result)

index.upsert(
    vectors=[
        {
            "id": "python-001",
            "values": [0.5, 0.3, 0.9],
            "metadata": {"language": "python", "topic": "Agentic AI"},
        },
        {
            "id": "python-002",
            "values": [0.8, 0.1, 0.6],
            "metadata": {"language": "python", "topic": "API Development"},
        },
    ],
    namespace="python-course",
)


index.upsert(
    vectors=[
        {
            "id": "javascript-001",
            "values": [0.9, 0.4, 0.6],
            "metadata": {"language": "javascript", "topic": "UI Development"},
        }
    ],
    namespace="javascript-course",
)


namespace_result = index.query(
    vector=query_vector, namespace="javascript-course", include_metadata=True, top_k=2
)

# print(namespace_result)

index.upsert(
    vectors=[
        {
            "id": "a-doc-1",
            "values": [0.1, 0.9, 0.3],
            "metadata": {"topic": "Python backend architecture", "language": "python"},
        },
        {
            "id": "a-doc-2",
            "values": [0.4, 0.7, 0.3],
            "metadata": {"topic": "FastAPI dependency injection", "language": "python"},
        },
    ],
    namespace="tenant-A",
)


index.upsert(
    vectors=[
        {
            "id": "b-doc-1",
            "values": [0.5, 0.1, 0.21],
            "metadata": {
                "topic": "Node.js Express middleware",
                "language": "javascript",
            },
        },
        {
            "id": "b-doc-2",
            "values": [0.1, 0.7, 0.2],
            "metadata": {
                "topic": "React frontend architecture",
                "language": "javascript",
            },
        },
    ],
    namespace="tenant-B",
)


tenant_a_result = index.query(
    vector=[0.1, 0.5, 0.3], include_metadata=True, top_k=2, namespace="tenant-A"
)

print(tenant_a_result.usage)
