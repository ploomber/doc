FROM python:3.11

COPY . .

RUN pip install -r requirements.txt --no-cache-dir

# THE FOLLOWING RUN COMMANDS ARE FOR DEMO PURPOSES ONLY!

# do not include the database file, if any
RUN rm -f db.sqlite3

# create the database tables
RUN python manage.py migrate

# create an admin user
RUN DJANGO_SUPERUSER_USERNAME=user \
    DJANGO_SUPERUSER_PASSWORD=pass \
    DJANGO_SUPERUSER_EMAIL="admin@example.com" \
    python manage.py createsuperuser --noinput

ENTRYPOINT ["gunicorn", "basicapp.wsgi", "run", "--bind", "0.0.0.0:80"]