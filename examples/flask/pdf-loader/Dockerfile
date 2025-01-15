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

RUN /venvs/app/bin/pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt /app/requirements.txt
RUN /venvs/app/bin/pip install -r /app/requirements.txt


COPY pdf-loader/ /app/pdf-loader
RUN /venvs/app/bin/pip install --editable /app/pdf-loader

COPY settings.py /app/settings.py
COPY entrypoint.py /app/entrypoint.py
COPY supervisord.conf /etc/supervisord.conf

# create tables
RUN /venvs/app/bin/python -m pdf_loader.db

# download models
RUN /venvs/app/bin/python -m pdf_loader.background

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]



