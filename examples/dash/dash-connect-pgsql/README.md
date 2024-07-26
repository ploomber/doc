# Dash App Connected to PostgreSQL Database

Interactive Dash Application, connected to PostgreSQL database.

![](app.png)

To use the app, fill in the environment variables (database parameters) in Dockerfile with the parameters from your PostgreSQL database. 

```DockerFile
FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/

RUN python3 -m pip install -r requirements.txt --no-cache-dir

COPY . /app

ENV PGHOST='YOUR_HOST'
ENV PGDATABASE='test'
ENV PGUSER='test_owner'
ENV PGPASSWORD='your_password'

RUN python3 upload.py

CMD ["gunicorn", "app:server", "run", "--bind", "0.0.0.0:80"]
```
