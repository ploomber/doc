from fastapi import FastAPI, UploadFile, File
from typing import Dict

import inference

app = FastAPI()


@app.post("/describe", response_model=Dict[str, str])
async def predict(file: UploadFile = File(...), question: str = ""):
    image_bytes = await file.read()
    response = inference.describe_image(image_bytes, question)
    return {"filename": question, "description": response}
