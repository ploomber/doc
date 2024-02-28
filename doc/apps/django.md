# Django

To deploy a Django application in Ploomber Cloud you need:

- A `Dockerfile`
- A Django project ([example](https://github.com/ploomber/doc/blob/main/examples/django/basic-app))


## `Dockerfile`

You need to provide a `Dockerfile`, you can use this [template](https://github.com/ploomber/doc/blob/main/examples/django/basic-app/Dockerfile) to get started. A basic `Dockerfile` looks like this:

```Dockerfile
FROM python:3.11

# copy source code files
COPY . .

# install dependencies
RUN pip install -r requirements.txt --no-cache-dir

# start app, the wsgi.py file is generated automatically when starting a Django project
ENTRYPOINT ["gunicorn", "basicapp.wsgi", "run", "--bind", "0.0.0.0:80"]
```

## Testing locally

To test your app, you can use `docker` locally:

```sh
# build the docker image
docker build . -t django

# run it
docker run -p 5000:80 django
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

Once you have all your files, create a zip file.

To deploy a Flask app from the deployment menu, follow these instructions:

![](../static/docker.png)