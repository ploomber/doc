import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
from io import BytesIO

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model_id = "vikhyatk/moondream2"
revision = "2024-03-05"
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    revision=revision,
    device_map="cuda" if torch.cuda.is_available() else None,
)

tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)


def describe_image(image, question):
    image_ = Image.open(BytesIO(image))
    enc_image = model.encode_image(image_).to(device)

    return model.answer_question(enc_image, question, tokenizer)
