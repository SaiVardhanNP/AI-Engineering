from transformers import AutoModelForImageSegmentation
from torchvision import transforms
from PIL import Image
import torch

# Load model
model = AutoModelForImageSegmentation.from_pretrained(
    "briaai/RMBG-2.0", trust_remote_code=True
)
torch.set_float32_matmul_precision("high")
model.eval()

# Load your image
image = Image.open("Dog.jpg")
original_size = image.size  # (width, height) — save this to resize the mask back later

# Preprocess: RMBG-2.0 expects a normalized 1024x1024 tensor
transform_image = transforms.Compose(
    [
        transforms.Resize((1024, 1024)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [1.0, 1.0, 1.0]),
    ]
)
input_tensor = transform_image(image.convert("RGB")).unsqueeze(0)  # add batch dimension

# Run inference
with torch.no_grad():
    preds = model(input_tensor)[
        -1
    ].sigmoid()  # model outputs a soft mask (0=background, 1=foreground)

# Postprocess: resize mask back to original image size
pred_mask = preds[0].squeeze()
mask_image = transforms.ToPILImage()(pred_mask)
mask_image = mask_image.resize(original_size)
mask_image.save("Dog_mask.png")

# Apply mask as alpha channel to cut out the background
image_rgba = image.convert("RGBA")
print("Original image size:", original_size)
print("Mask size:", mask_image.size)
print("Mask mode:", mask_image.mode)
image_rgba.putalpha(mask_image)

# Save result — transparent PNG with background removed
image_rgba.save("Dog_no_bg.png")
print("Saved Dog_no_bg.png")
