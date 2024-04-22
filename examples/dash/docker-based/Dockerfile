FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir

COPY . /app

CMD ["gunicorn", "app:server", "run", "--bind", "0.0.0.0:80"]
