FROM python:3.11-slim-bookworm

WORKDIR /srv

COPY requirements.txt /srv/

RUN pip install -r requirements.txt --no-cache-dir

COPY . /srv

CMD ["voila", "--port=80", "--no-browser", "app.ipynb", "--Voila.ip='0.0.0.0'"]
