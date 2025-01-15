# PDF loader

An app to parse and search over PDFs.

```sh
# create the environment and install the required dependencies
conda create --name pdf-loader python=3.12 rabbitmq-server -c conda-forge -y

# activate environment
conda activate pdf-loader

# install torch cpu
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu


# install the package and requirements
pip install --editable pdf-loader
pip install -r requirements.txt

# create tables
python -m pdf_loader.db

# start app
python -m pdf_loader.app
# open: http://localhost:5000

# to start celery
rabbitmq-server

celery --app pdf_loader.background worker --loglevel=INFO --pool=prefork --concurrency=1
```

With Docker:

```sh
docker build -t pdf-loader .

# http://localhost:5000
docker run -p 5000:80 --env-file .env pdf-loader

docker run -it pdf-loader bash
```

