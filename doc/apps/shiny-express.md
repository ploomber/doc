# Shiny Express

To deploy a [Shiny Express](https://shiny.posit.co/blog/posts/shiny-express/) application to Ploomber Cloud you need:

- A `Dockerfile`
- A Shiny Express project

## `Dockerfile`

Use this [template](https://github.com/ploomber/doc/blob/main/examples/docker/shiny-express/Dockerfile) `Dockerfile`:

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
docker build . -t shiny-express-app

# run it
docker run -p 5000:80 shiny-express-app
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

Once you have all your files, create a zip file.

To deploy a Shiny Express app from the deployment menu, select the Docker option and follow the instructions:

![](../static/docker.png)