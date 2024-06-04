# we need pyotrch==2.3.0 for vllm==0.4.3
FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-devel

WORKDIR /srv

COPY requirements.txt /srv/
RUN pip install -r requirements.txt --no-cache-dir

COPY . /srv

# NOTE: some models require accepting a license. If that's your case
# ensure you pass your HF_TOKEN as a secret when deploying the project
ENTRYPOINT ["python", "-m", "vllm.entrypoints.openai.api_server", "--host", "0.0.0.0", "--port", "80", "--model", "facebook/opt-125m", "--dtype=half"]