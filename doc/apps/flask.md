# Flask

To deploy a Flask application in Ploomber Cloud you need:

- A `Dockerfile`
- Your code
## `Dockerfile`

You need to provide a `Dockerfile`, you can use this [template](https://github.com/ploomber/doc/blob/main/examples/docker/flask/Dockerfile) to get started. The template contains the minimal steps needed for a deployment but you need to modify so it installs any required dependencies and copies your code into the Docker image.

```Dockerfile
FROM python:3.11

# assumes app.py contains your flask app
COPY app.py app.py
# install flask and gunicorn
RUN pip install flask gunicorn

# this configuration is needed for your app to work, do not change it
ENTRYPOINT ["gunicorn", "app:app", "run", "--bind", "0.0.0.0:80"]
```

## Testing locally

To test your app, you can use `docker` locally:

```sh
# build the docker image
docker build . -t flask

# run it
docker run -p 5000:80 flask
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

Once you have all your files, create a zip file.

To deploy a Flask app from the deployment menu, follow these instructions:

![](../static/docker.png)