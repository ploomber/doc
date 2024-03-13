FROM python:3.11-slim

RUN pip install mlflow



ENTRYPOINT ["mlflow", "server", "--host", "0.0.0.0", "--port", "80", "--app-name", "basic-auth"]