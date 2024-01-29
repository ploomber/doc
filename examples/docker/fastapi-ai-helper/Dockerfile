FROM python:3.11

COPY app.py app.py
COPY .env .env
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --index-url https://download.pytorch.org/whl/cpu

ENTRYPOINT ["uvicorn", "app:app", "--host=0.0.0.0", "--port=80"]
