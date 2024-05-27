FROM python:3.11-slim-bookworm

WORKDIR /srv

COPY requirements.txt /srv/
RUN pip install -r requirements.txt --no-cache-dir

COPY . /srv

# Run the application
CMD ["python", "app.py"]
