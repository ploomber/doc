# Dash

To deploy a [Dash](https://dash.plotly.com/) application to Ploomber Cloud you need:

- A `Dockerfile`
- A Dash project

## `Dockerfile`

Use this [template](https://github.com/ploomber/doc/blob/main/examples/dash/simple-app/Dockerfile) `Dockerfile`:

```Dockerfile
FROM python:3.11

COPY app.py app.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "app:server", "run", "--bind", "0.0.0.0:80"]
```

## Testing locally

To test your app, you can use `docker` locally:

```sh
# build the docker image
docker build . -t dash-app

# run it
docker run -p 5000:80 dash-app
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

Once you have all your files, create a zip file.

To deploy a Dash app from the deployment menu, select the Docker option and follow the instructions:

![](../static/docker.png)