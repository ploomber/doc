FROM python:3.11

COPY app.py app.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

ENTRYPOINT ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "80"]
