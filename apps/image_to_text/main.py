from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image

model_path = "./modes/vit-gpt2-image-captioning"

model = VisionEncoderDecoderModel.from_pretrained(model_path)
feature_extractor = ViTImageProcessor.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Fix pad_token issue
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.pad_token_id

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

gen_kwargs = {
    "max_length": 16,
    "num_beams": 4,
    "early_stopping": True,
    "no_repeat_ngram_size": 2,
}

def predict_step(image_paths):
    images = [Image.open(p).convert("RGB") for p in image_paths]

    # Only pixel_values are produced by ViTImageProcessor
    encoding = feature_extractor(images=images, return_tensors="pt")
    pixel_values = encoding.pixel_values.to(device)

    with torch.no_grad():
        output_ids = model.generate(
            pixel_values=pixel_values,
            **gen_kwargs
        )

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    return [p.strip() for p in preds]


print(predict_step(["./Images/Office.jpg"]))