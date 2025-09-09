FROM python:3.12-slim-bookworm

WORKDIR /srv

# Install Dash and Gunicorn
RUN pip install dash gunicorn --no-cache-dir


COPY requirements.txt /srv/

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "-b", "0.0.0.0:80", "app:server"]
