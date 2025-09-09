FROM python:3.12-slim-bookworm

WORKDIR /srv

# Install Flask & Gunicorn
RUN pip install flask gunicorn --no-cache-dir

COPY requirements.txt /srv/

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# CMD to run the Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]
