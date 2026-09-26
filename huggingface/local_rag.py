from pypdf import PdfReader
from transformers import pipeline


# --------------------------------
# 1. Extract PDF text
# --------------------------------

reader = PdfReader("Engineering.pdf")

document_text = ""

for page in reader.pages:
    text = page.extract_text()

    if text:
        document_text += text + "\n"


# --------------------------------
# 2. Create simple chunks
# --------------------------------

chunk_size = 500
overlap = 100

words = document_text.split()

chunks = []

start = 0

while start < len(words):
    end = start + chunk_size

    chunk = " ".join(words[start:end])

    chunks.append(chunk)

    start = end - overlap


print("Number of chunks:", len(chunks))


# --------------------------------
# 3. Select some context
# --------------------------------

context = "\n\n".join(chunks[:3])

print("\n===== CONTEXT =====")
print(context)


# --------------------------------
# 4. User question
# --------------------------------

question = "What projects are included in this curriculum?"


# --------------------------------
# 5. Build RAG prompt
# --------------------------------

prompt = f"""
Answer the question using only the provided context.

Context:
{context}

Question:
{question}

Answer:
"""


# --------------------------------
# 6. Load local Gemma
# --------------------------------

pipe = pipeline(
    "text-generation",
    model="google/gemma-3-1b-it"
)


# --------------------------------
# 7. Generate answer
# --------------------------------

result = pipe(
    prompt,
    max_new_tokens=50
)


# --------------------------------
# 8. Print answer
# --------------------------------

print("\n===== ANSWER =====")
generated = result[0]["generated_text"]

print(generated)