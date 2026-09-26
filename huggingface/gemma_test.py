from transformers import pipeline


pipe = pipeline("text-generation", model="google/gemma-3-1b-it")


messages = [{"role": "user", "content": "Explain Semantic Search in simple terms."}]

result = pipe(messages, max_new_tokens=40)


print(result[0]["generated_text"][-1]["content"])
