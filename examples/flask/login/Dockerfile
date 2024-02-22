FROM python:3.11

COPY . .
RUN pip install -r requirements.txt
RUN python models.py

ENTRYPOINT ["gunicorn", "app:app", "run", "--bind", "0.0.0.0:80"]