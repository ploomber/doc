FROM python:3.11

COPY app.py app.py
COPY chainlit.md chainlit.md
RUN pip install chainlit --no-cache-dir

ENTRYPOINT ["chainlit", "run", "app.py", "--host=0.0.0.0", "--port=80", "--headless"]