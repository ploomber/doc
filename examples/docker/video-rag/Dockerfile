FROM python:3.11

COPY app.py app.py
COPY chat.py chat.py
COPY .env .env
COPY requirements.txt requirements.txt
COPY static/ static/
RUN pip install -r requirements.txt
RUN apt install ffmpeg


ENTRYPOINT ["solara", "run", "app.py", "--host=0.0.0.0", "--port=80"]