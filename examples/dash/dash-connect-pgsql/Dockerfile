FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/

RUN python3 -m pip install -r requirements.txt --no-cache-dir

COPY . /app

CMD ["gunicorn", "app:server", "run", "--bind", "0.0.0.0:80"]
