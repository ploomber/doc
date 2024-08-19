FROM python:3.11

RUN apt-get update 

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt --no-cache-dir

ENTRYPOINT ["uvicorn", "app:app", "--host=0.0.0.0", "--port=80"]
