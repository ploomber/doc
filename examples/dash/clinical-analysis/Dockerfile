FROM python:3.11

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "app:server", "run", "--bind", "0.0.0.0:80"]
