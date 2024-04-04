FROM python:3.11

COPY app.py app.py
COPY chainlit.md chainlit.md
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# do not change the arguments
ENTRYPOINT ["chainlit", "run", "app.py", "--host=0.0.0.0", "--port=80", "--headless"]