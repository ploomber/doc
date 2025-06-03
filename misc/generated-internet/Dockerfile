# Dockerfile
FROM python:3.12-slim-bookworm
WORKDIR /srv

# Install Python dependencies
COPY requirements.txt /srv/
RUN pip install -r requirements.txt --no-cache-dir

# Copy the application
COPY . /srv

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV BLOCK_REDOWNDLOAD=True

# Expose ports
EXPOSE 80

CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
