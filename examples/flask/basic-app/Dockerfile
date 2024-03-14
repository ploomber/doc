FROM python:3.11

COPY app.py app.py
RUN pip install flask gunicorn --no-cache-dir

ENTRYPOINT ["gunicorn", "app:app", "run", "--bind", "0.0.0.0:80"]
