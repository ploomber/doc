FROM python:3.11

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["voila", "app.ipynb", "--no-browser", "--port=80", "--Voila.ip='0.0.0.0'", "--template=gridstack"]
