FROM python:3.11

COPY app.py app.py
RUN pip install solara


ENTRYPOINT ["solara", "run", "app.py", "--host=0.0.0.0", "--port=80", "--log-level=debug", "--log-level-uvicorn=debug", "--root-path=/__PROJECT_ID__"]