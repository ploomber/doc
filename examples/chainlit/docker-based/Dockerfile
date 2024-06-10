FROM python:3.11-slim-bookworm

WORKDIR /srv

COPY requirements.txt /srv/
COPY . /srv

RUN pip install chainlit --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

ENTRYPOINT ["chainlit", "run", "app.py", "--host=0.0.0.0", "--port=80", "--headless"]