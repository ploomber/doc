FROM python:3.11

COPY app.py app.py
COPY pipelinehelper.py pipelinehelper.py
COPY data.csv data.csv
COPY .env .env
COPY requirements.txt requirements.txt
RUN pip install torch==2.1.1 torchvision==0.16.1 --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

ENTRYPOINT ["uvicorn", "app:app", "--host=0.0.0.0", "--port=80"]
