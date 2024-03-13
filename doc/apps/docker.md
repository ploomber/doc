# Docker

To deploy a Docker-based web application in Ploomber Cloud you need:

- A `Dockerfile`
- Your code
## `Dockerfile`

You need to provide a `Dockerfile`, you can use this [flask-based template](https://github.com/ploomber/doc/blob/main/examples/flask/basic-app/Dockerfile) to get started.

For a successful deployment, you app must run in port 80.

Here's an example using flask:

```Dockerfile
FROM python:3.11

COPY app.py app.py
RUN pip install flask gunicorn

ENTRYPOINT ["gunicorn", "app:app", "run", "--bind", "0.0.0.0:80"]
```

Once you have all your files, `.zip` them. For example, a simple app will contain two files:

- `Dockerfile`
- `app.py`

## Testing locally

To test your app, you can use `docker` locally:

```sh
# build the docker image
docker build . -t myapp

# run it
docker run -p 5000:80 myapp
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

To deploy the app from the deployment menu, follow these instructions:

![](../static/docker.png)


```{tip}
To ensure your app doesn't break on re-deployments, pin your [dependencies.](pin-dependencies)
```