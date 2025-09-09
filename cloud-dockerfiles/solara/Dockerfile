FROM python:3.12-slim-bookworm

WORKDIR /srv

RUN pip install solara --no-cache-dir

COPY requirements.txt /srv/

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir


# CMD to run the Solara app from /srv/app
CMD ["solara", "run", "/srv/app.py", "--port=80", "--host=0.0.0.0", "--production"]
