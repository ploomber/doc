# Hubspot Explorer

An app to help customer support reps by summarizing similar tickets from HubSpot.

```sh
# create the environment and install the required dependencies
conda create --name hubspot python rabbitmq-server -c conda-forge -y

# install the package
pip install --editable hubspot-loader

# create tables
python -m hubspot_loader.db

# load documents
python -m hubspot_loader.load 

# start app
python -m hubspot_loader.app
# open: http://localhost:5000

# to start celery
rabbitmq-server

celery --app hubspot_loader.background worker --loglevel=INFO --pool=prefork --concurrency=1 --beat
```

With Docker:

```sh
docker build -t hubspot .

# http://localhost:5000
docker run -p 5000:80 --env-file .env hubspot

docker run -it hubspot bash
```

