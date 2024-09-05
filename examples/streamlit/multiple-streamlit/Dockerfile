FROM --platform=linux/amd64 python:3.12-slim

RUN apt-get update && \
    apt-get install -y \
    supervisor nginx \
    && rm -rf /var/lib/apt/lists/*


RUN python -m venv /venvs/first
RUN python -m venv /venvs/second

COPY apps/requirements-first.txt /apps/requirements-first.txt
COPY apps/requirements-second.txt /apps/requirements-second.txt

RUN /venvs/first/bin/pip install -r /apps/requirements-first.txt
RUN /venvs/second/bin/pip install -r /apps/requirements-second.txt

COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisord.conf

COPY apps/ /apps

EXPOSE 80


CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]