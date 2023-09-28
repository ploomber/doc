# FastAPI

To deploy a FastAPI application in Ploomber Cloud you need:

- A `Dockerfile`
- Your code

## `Dockerfile`

You need to provide a `Dockerfile`, you can use this [template](https://github.com/ploomber/doc/blob/main/examples/docker/fastapi/Dockerfile) to get started. The template contains the minimal steps needed for a deployment but you need to modify so it installs any required dependencies and copies your code into the Docker image.

```Dockerfile
FROM python:3.11

# assumes app.py contains your fastapi app
COPY app.py app.py
# install dependencies
RUN pip install fastapi uvicorn

# this configuration is needed for your app to work, do not change it
ENTRYPOINT ["uvicorn", "app:app", "--host=0.0.0.0", "--port=80", "--root-path=/__PROJECT_ID__"]
```

Once you have all your files, create a zip file.

## Deploy

To deploy a Flask app from the deployment menu, follow these instructions:

![](../static/docker.png)


## Running locally

You can test your app locally with:

```sh
uvicorn app:app --port 8000
```

Note that your app will be served from `http://127.0.0.1:8000/__PROJECT_ID__/`