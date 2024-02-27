FROM python:3.11

COPY app.py app.py
RUN pip install gradio

ENV GRADIO_SERVER_PORT=80
ENV GRADIO_SERVER_NAME=0.0.0.0

ENTRYPOINT ["gradio", "app.py"]