FROM python:3.11

COPY api/ /api/
COPY client/ /client/
COPY start.sh start.sh
COPY requirements.txt requirements.txt
COPY .env .env

RUN apt-get update && apt-get -y install redis-server
RUN pip install -r requirements.txt --no-cache-dir
RUN python api/create_models.py

ENTRYPOINT ["sh", "start.sh", "--port", "80"]