FROM python:3.11

COPY app.py app.py
RUN pip install fastapi uvicorn --no-cache-dir

ENTRYPOINT ["uvicorn", "app:app", "--host=0.0.0.0", "--port=80"]
