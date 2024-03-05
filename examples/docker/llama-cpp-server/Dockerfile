FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

WORKDIR /srv

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY model_downloader.py .
RUN python model_downloader.py --repo_id TheBloke/Llama-2-7b-Chat-GGUF --filename llama-2-7b-chat.Q4_0.gguf --save_dir ./models

RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install 'llama-cpp-python[server]'

WORKDIR /srv
ENTRYPOINT ["python", "-m", "llama_cpp.server", "--model", "./models/llama-2-7b-chat.Q4_0.gguf", "--port", "80", "--host", "0.0.0.0", "--n_gpu_layers", "1000"]
