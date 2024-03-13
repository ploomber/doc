FROM python:3.11-slim-bookworm

RUN pip install panel --no-cache-dir

WORKDIR /usr/local/lib/python3.11/site-packages/matplotlib/mpl-data/fonts/ttf
RUN apt update && apt install -y wget
RUN wget https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf

WORKDIR /srv
COPY requirements.txt /srv/
RUN pip install -r requirements.txt --no-cache-dir

WORKDIR /srv
COPY . /srv

ENTRYPOINT ["panel", "serve", "app.py", "--port=80", "--address=0.0.0.0", "--allow-websocket-origin=*"]

