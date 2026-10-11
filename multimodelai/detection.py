from PIL import Image
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from transformers import pipeline


image = Image.open("detection.png")

# processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")

# model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

# inputs = processor(images=image, return_tensors="pt")

# with torch.no_grad():
#     outputs = model(**inputs)

# target_sizes = torch.tensor([image.size[::-1]])

# results = processor.post_process_object_detection(
#     outputs, target_sizes=target_sizes, threshold=0.1
# )[0]


# for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
#     print(f"{model.config.id2label[label.item()]} {score.item():2f} {box.tolist()}")


detector = pipeline("object-detection", model="facebook/detr-resnet-50")
results = detector("detection.png", threshold=0.5)

for r in results:
    print(f"{r['label']}: {r['score']:.2f} {r['box']}")
