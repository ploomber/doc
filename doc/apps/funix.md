# Funix

```{note}
[Click here](https://gentle-heart-9135.ploomberapp.io/) to see a live Funix demo!
```

To deploy a [Funix](https://github.com/TexteaInc/funix) application in Ploomber Cloud you need:

- A `Dockerfile`
- Your code

## `Dockerfile`

You need to provide a `Dockerfile`, you can use this [template](https://github.com/ploomber/doc/blob/main/examples/docker/funix/Dockerfile) to get started. The template contains the minimal steps needed for a deployment but you need to modify so it installs any required dependencies and copies your code into the Docker image.

```Dockerfile
FROM python:3.11

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py

# important: your app must run in port 80!
ENTRYPOINT ["funix", "-l", "--host=0.0.0.0", "--port=80", "app.py"]
```

## Testing locally

To test your app, you can use `docker` locally:

```sh
# build the docker image
docker build . -t funix

# run it
docker run -p 5000:80 funix
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

Once you have all your files, create a zip file.

To deploy a Funix app from the deployment menu, follow these instructions:

![](../static/docker.png)