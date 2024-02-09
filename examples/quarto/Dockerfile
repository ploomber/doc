FROM python:3.11

COPY _site/ _site/
ENTRYPOINT ["python", "-m", "http.server", "80", "--bind", "0.0.0.0", "--directory", "_site"]
