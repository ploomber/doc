FROM python:3.11

COPY app.py app.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "app:server", "run", "--bind", "0.0.0.0:80"]
