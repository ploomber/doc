# Shiny (Python)

To deploy a [Shiny](https://shiny.posit.co/py/docs/overview.html) Python application to Ploomber Cloud you need:

- A [Ploomber Cloud](https://platform.ploomber.io/register) account
- A `Dockerfile`
- A Shiny Python project

## `Dockerfile`

Use this [template](https://github.com/ploomber/doc/blob/main/examples/shiny/basic-app/Dockerfile) `Dockerfile`:

```Dockerfile
FROM python:3.11

COPY app.py app.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "80"]
```

## Testing locally

To test your app, you can use `docker` locally:

```sh
# build the docker image
docker build . -t shiny-app

# run it
docker run -p 5000:80 shiny-app
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

Once you have all your files, create a zip file.

To deploy a Shiny app from the deployment menu, select the Docker option and follow the instructions:

![](../static/docker.png)


```{tip}
To ensure your app doesn't break on re-deployments, pin your [dependencies.](pin-dependencies)
```