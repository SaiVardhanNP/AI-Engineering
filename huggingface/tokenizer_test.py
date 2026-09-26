from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
import torch

model_id = "google/gemma-3-1b-it"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

text = "Explain RAG in simple terms"

inputs = tokenizer(text, return_tensors="pt")


with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=40)

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(response)


print(response)
