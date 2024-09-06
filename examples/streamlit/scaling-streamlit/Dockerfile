FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app
EXPOSE 80

RUN apt-get update && \
    apt-get install -y \
    supervisor redis-server \
    && rm -rf /var/lib/apt/lists/*


RUN pip install streamlit rq

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt --no-cache-dir

COPY supervisord.conf /etc/supervisord.conf
COPY . /app/

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]