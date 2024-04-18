FROM python:3.11

COPY example.py example.py
RUN pip install marimo pandas matplotlib --no-cache-dir

ENTRYPOINT ["marimo", "edit", "--host", "0.0.0.0", "--port", "80", "--headless"]
