from pinecone import Pinecone, ServerlessSpec
from config import settings


pc = Pinecone(api_key=settings.pinecone_api_key)

if not pc.has_index(settings.pinecone_index_name):
    pc.create_index(
        name=settings.pinecone_index_name,
        dimension=3072,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",
        ),
    )


print(pc.describe_index(settings.pinecone_index_name))
