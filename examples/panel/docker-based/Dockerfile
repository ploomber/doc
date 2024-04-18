FROM python:3.11-slim-bookworm

WORKDIR /app

RUN pip install panel --no-cache-dir

COPY . /app

CMD ["panel", "serve", "app.py", "--port=80", "--address=0.0.0.0", "--allow-websocket-origin=*"]

