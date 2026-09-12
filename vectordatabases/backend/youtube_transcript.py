from youtube_transcript_api import YouTubeTranscriptApi
import re
from vectordatabases.services.embedding_service import EmbeddingService
from vectordatabases.services.pinecone_repository import PineconeRepository
from geminiClient import client

api = YouTubeTranscriptApi()
embedding_service = EmbeddingService()
pinecone = PineconeRepository()


def clean_transcript(raw_transcript):
    cleaned_segments = []

    for snippet in raw_transcript:
        text = snippet.text

        text = text.strip()

        text = re.sub(r"\s+", " ", text)

        if not text:
            continue

        cleaned_segment = {
            "text": text,
            "start": snippet.start,
            "end": round(snippet.start + snippet.duration, 3),
        }
        cleaned_segments.append(cleaned_segment)

    return cleaned_segments


def build_context(results):
    formatted_chunks = [f"[{r['start']} - {r['end']}]\n{r['text']}" for r in results]
    return "\n\n".join(formatted_chunks)


def prompt_builder(context, question):
    prompt = f"""You are answering questions about a YouTube video.
    
    Use ONLY the provided transcript context.
    
    If the answer cannot be found in the context,
    say that the information was not found in the transcript.
    Do not use outside knowledge.
    
    Transcript context:
    {context}
    
    Question:
    {question}"""

    return prompt


def chunk_transcript(segments, chunk_size, overlap):
    chunks = []
    current_segments = []
    current_word_count = 0

    for segment in segments:
        segment_word_count = len(segment["text"].split())
        current_segments.append(segment)
        current_word_count += segment_word_count  # Fixed typo here

        if current_word_count >= chunk_size:
            chunk = {
                "text": " ".join(s["text"] for s in current_segments),
                "start": current_segments[0]["start"],
                "end": current_segments[-1]["end"],
            }
            chunks.append(chunk)

            # Build the overlapping window from the tail
            overlap_segments = []
            overlap_word_count = 0

            for seg in reversed(current_segments):
                overlap_segments.insert(0, seg)
                overlap_word_count += len(seg["text"].split())

                if overlap_word_count >= overlap:
                    break

            current_segments = overlap_segments
            current_word_count = overlap_word_count

    # Only create a tail chunk if there is new text beyond the last overlap
    if current_segments and current_word_count > overlap:
        chunks.append(
            {
                "text": " ".join(s["text"] for s in current_segments),
                "start": current_segments[0]["start"],
                "end": current_segments[-1]["end"],
            }
        )

    return chunks


transcript = api.fetch("ZHCB09O6zUk")

snippets = clean_transcript(transcript)


chunks = chunk_transcript(snippets, chunk_size=80, overlap=20)

texts = [chunk["text"] for chunk in chunks]


embeddings = embedding_service.embed_documents(texts)

pinecone.upsert_chunks(
    chunks=chunks,
    embeddings=embeddings,
    video_id="ZHCB09O6zUk",
)


query = "What is the Turing Test?"

query_embedding = embedding_service.embed_query(query)

results = pinecone.search(
    query_embedding=query_embedding,
    video_id="ZHCB09O6zUk",
    top_k=3,
)

context = build_context(results)

# print(context)

response = client.models.generate_content(
    model="gemini-3.5-flash-lite", contents=prompt_builder(context, query)
)

print(response.text)
