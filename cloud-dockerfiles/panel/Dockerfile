FROM python:3.12-slim-bookworm

WORKDIR /srv

# Install Panel
RUN pip install panel --no-cache-dir


COPY requirements.txt /srv/

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# CMD to run the Panel app
CMD ["panel", "serve", "app.py", "--port=80", "--address=0.0.0.0", "--allow-websocket-origin=*"]
