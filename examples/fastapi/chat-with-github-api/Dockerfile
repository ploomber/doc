FROM python:3.11

COPY app.py app.py
COPY database.py database.py
COPY models.py models.py
COPY task.py task.py
COPY start.sh start.sh
COPY requirements.txt requirements.txt
COPY .env .env

RUN apt-get update && apt-get -y install redis-server
RUN pip install -r requirements.txt --no-cache-dir
RUN python models.py

ENTRYPOINT ["sh", "start.sh", "--port", "80"]