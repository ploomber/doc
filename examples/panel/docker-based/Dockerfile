FROM python:3.11-slim-bookworm

WORKDIR /srv

COPY requirements.txt /srv/
RUN pip install -r requirements.txt --no-cache-dir

COPY . /srv

CMD ["panel", "serve", "app.py", "--port=80", "--address=0.0.0.0", "--allow-websocket-origin=*"]

