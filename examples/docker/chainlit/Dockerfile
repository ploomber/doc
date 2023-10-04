FROM python:3.11

COPY app.py app.py
RUN pip install chainlit


ENTRYPOINT ["chainlit", "run", "app.py", "--host=0.0.0.0", "--port=80", "--headless"]