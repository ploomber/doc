# we need pyotrch==2.1.2 for vllm==0.3.3
FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-devel

WORKDIR /srv

COPY requirements.txt /srv/
RUN pip install -r requirements.txt --no-cache-dir

COPY . /srv

# NOTE: this requires HF_TOKEN so the model can be downloaded. The account associated
# with the token must have access to the google/gemma-2b-it model.
# ENTRYPOINT ["python", "-m", "vllm.entrypoints.openai.api_server", "--host", "0.0.0.0", "--port", "80", "--model", "google/gemma-2b-it", "--dtype=half"]
ENTRYPOINT ["python", "-c", "while True: pass"]