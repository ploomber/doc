FROM python:3.11

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py

ENTRYPOINT ["funix", "-l", "--host=0.0.0.0", "--port=80", "app.py"]

