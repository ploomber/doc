FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Configure the container
EXPOSE 80
ENTRYPOINT ["gunicorn", "app:app", "--bind", "0.0.0.0:80"] 