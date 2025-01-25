FROM python:3.12-slim

WORKDIR /app

RUN pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:80", "--config", "gunicorn.conf.py"]
