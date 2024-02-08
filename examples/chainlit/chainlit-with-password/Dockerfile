FROM python:3.11

RUN pip install chainlit
COPY chainlit.md chainlit.md
COPY app.py app.py


ENTRYPOINT ["chainlit", "run", "app.py", "--host=0.0.0.0", "--port=80", "--headless"]