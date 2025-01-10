# NOTE: could not get sqlite-vec to work on arm64
# --platform=linux/amd64
FROM python:3.12-slim

WORKDIR /app

# install pre-requisites
RUN apt-get update && \
    apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*


# install rabbitmq
RUN apt-get update && \
    apt-get install -y rabbitmq-server && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /venvs/app

COPY requirements.txt /app/requirements.txt
RUN /venvs/app/bin/pip install -r /app/requirements.txt


COPY gdrive-loader/ /app/gdrive-loader
RUN /venvs/app/bin/pip install --editable /app/gdrive-loader

COPY settings.py /app/settings.py
COPY entrypoint.py /app/entrypoint.py
COPY supervisord.conf /etc/supervisord.conf

RUN /venvs/app/bin/python -m gdrive_loader.db

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]



