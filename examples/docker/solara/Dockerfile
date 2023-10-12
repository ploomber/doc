FROM python:3.11

COPY app.py app.py
RUN pip install solara altair vega_datasets pandas


ENTRYPOINT ["solara", "run", "app.py", "--host=0.0.0.0", "--port=80"]