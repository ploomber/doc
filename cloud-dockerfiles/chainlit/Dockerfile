FROM python:3.12-slim-bookworm

WORKDIR /srv

# Install base requirements first
RUN pip install chainlit --no-cache-dir

# Copy only the requirements
COPY requirements.txt /srv/

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# CMD to run the Chainlit app
CMD ["chainlit", "run", "/srv/app.py", "--host=0.0.0.0", "--port=80", "--headless"]
