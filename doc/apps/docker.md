# Docker

To deploy a Docker-based web application in Ploomber Cloud you need:

- A `Dockerfile`
- Your code
## `Dockerfile`

You need to provide a `Dockerfile`, you can use this [flask-based template](https://github.com/ploomber/doc/blob/main/examples/docker/flask/Dockerfile) to get started.

For a successful deployment, you need the following:

- Your app must run in port 80
- You'll be assigned a  `ploomberapp.io/{{PROJECT_ID}}` URL, hence, your app must accept requests from the `/{{PROJECT_ID}}` path.

Here's an example using flask:

```Dockerfile
FROM python:3.11

# assumes app.py contains your flask app
COPY app.py app.py
# install flask and gunicorn
RUN pip install flask gunicorn

# this configuration is needed for your app to work, do not change it
ENTRYPOINT ["gunicorn", "app:app", "run", "--bind", "0.0.0.0:80", "--env", "SCRIPT_NAME=/{{PROJECT_ID}}"]
```

Once you have all your files, create a zip file.

## Deploy

To deploy the app from the deployment menu, follow these instructions:

![](../static/docker.png)