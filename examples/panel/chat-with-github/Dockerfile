FROM python:3.11

COPY app.py app.py
COPY base.py base.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["panel", "serve", "base.py", "--address=0.0.0.0", "--port=80"]
