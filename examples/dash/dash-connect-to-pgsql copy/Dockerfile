FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/

RUN python3 -m pip install -r requirements.txt --no-cache-dir

COPY . /app

ENV PGHOST='ep-delicate-union-a4m0ybm6.us-east-1.aws.neon.tech'
ENV PGDATABASE='test'
ENV PGUSER='test_owner'
ENV PGPASSWORD='KTQvScsA9P0j'

RUN python3 upload.py

CMD ["gunicorn", "app:server", "run", "--bind", "0.0.0.0:80"]
