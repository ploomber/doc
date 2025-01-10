# Google Drive Explorer

This app allows loading documents from Google Drive and answering questions about them.

```sh
# create the environment and install the required dependencies
conda create --name gdrive python rabbitmq-server -c conda-forge -y

# install the package
pip install --editable gdrive-loader

# to generate .env file
python -m gdrive_loader.env

# create tables
python -m gdrive_loader.db

# start app (and login to create users)
python -m gdrive_loader.app
# open: http://localhost:5000

# load documents
python -m gdrive_loader.load --email EMAIL --limit 20


# to start celery
rabbitmq-server

celery --app gdrive_loader.background worker --loglevel=INFO --pool=prefork --concurrency=1 --beat
```

With Docker:

```sh
docker build -t gdrive .

# http://localhost:5000
docker run -p 5000:80 --env-file .env gdrive

docker run -it gdrive bash
```

