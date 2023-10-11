FROM python:3.11

COPY app.py app.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["panel", "serve", "app.py", "--port=80", "--address=0.0.0.0", "--allow-websocket-origin=__PROJECT_ID__.ploomberapp.io"]