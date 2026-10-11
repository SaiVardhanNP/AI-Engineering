from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch
import torch.nn.functional as F

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
image = Image.open("Dog.jpg")

texts = [
    "a domestic animal",
    "a wild animal",
    "a vehicle"
]
inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)

outputs = model(**inputs)

print(outputs.image_embeds.shape)
print(outputs.text_embeds.shape)

image_embeddings = outputs.image_embeds
text_embeddings = outputs.text_embeds

image_embeddings = F.normalize(image_embeddings, p=2, dim=-1)

text_embeddings = F.normalize(text_embeddings, p=2, dim=-1)

similarities = image_embeddings @ text_embeddings.T

print(similarities)

best_index = similarities.argmax().item()

print(texts[best_index])
