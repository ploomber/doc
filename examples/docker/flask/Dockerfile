FROM python:3.11

COPY app.py app.py
RUN pip install flask gunicorn

ENTRYPOINT ["gunicorn", "app:app", "run", "--bind", "0.0.0.0:80", "--env", "SCRIPT_NAME=/{{PROJECT_ID}}"]
