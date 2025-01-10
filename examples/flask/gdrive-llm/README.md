```sh
conda create --name gdrive python -c conda-forge -y
conda install rabbitmq-server -c conda-forge -y


# create tables
python -m gdrive_loader.db

# start app (and login to create users)
python -m gdrive_loader.app
# open: http://localhost:5000

# load documents
python -m gdrive_loader.load --email EMAIL --limit 20


rabbitmq-server
celery --app gdrive_loader.background worker --loglevel=INFO --pool=prefork --concurrency=1 --beat
```

```sh
docker build -t gdrive .

python -m gdrive_loader.encode

# http://localhost:5000
docker run -p 5000:80 --env-file .env gdrive

docker run -it gdrive bash
```

