# Streamlit

To deploy a Streamlit application in Ploomber Cloud you need:

- A `Dockerfile`
- Your code

## `Dockerfile`

You need to provide a `Dockerfile`, you can use this [template](https://github.com/ploomber/doc/blob/main/examples/docker/streamlit/Dockerfile) to get started. The template contains the minimal steps needed for a deployment but you need to modify so it installs any required dependencies and copies your code into the Docker image.

```Dockerfile
FROM python:3.11

COPY app.py app.py

RUN pip install streamlit

ENTRYPOINT ["streamlit", "run", "app.py", \
            # do not change these values
            "--server.port=80", \
            "--server.headless=true", \
            "--server.address=0.0.0.0", \
            "--browser.gatherUsageStats=false", \
            "--server.enableStaticServing=true", \
            "--server.fileWatcherType=none", \
            "--client.toolbarMode=viewer"]
```

## Testing locally

To test your app, you can use `docker` locally:

```sh
# build the docker image
docker build . -t streamlit

# run it
docker run -p 5000:80 streamlit
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

Once you have all your files, create a zip file.

To deploy a Flask app from the deployment menu, follow these instructions:

![](../static/docker.png)