FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

WORKDIR /srv
COPY requirements.txt /srv/
RUN pip install -r requirements.txt --no-cache-dir

COPY . /srv

# CMD ["python", "-c", "while True: pass"]
# CMD ["solara", "run", "app.py", "--port=80", "--host=0.0.0.0", "--production" ]

ENTRYPOINT ["uvicorn", "app:app", "--host=0.0.0.0", "--port=80"]