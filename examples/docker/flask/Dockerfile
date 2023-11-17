FROM python:3.11

COPY app.py app.py
COPY walmart_sales_rf.joblib walmart_sales_rf.joblib
COPY static/ static/
COPY templates/ templates/
RUN pip install flask gunicorn numpy pandas scikit-learn

ENTRYPOINT ["gunicorn", "app:app", "run", "--bind", "0.0.0.0:80", "--env", "SCRIPT_NAME=/__PROJECT_ID__"]
