FROM python:3.11

COPY app-core.py app-core.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["shiny", "run", "app-core.py", "--host", "0.0.0.0", "--port", "80"]
