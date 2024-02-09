# Shiny (R)

To deploy a [Shiny](https://shiny.posit.co/py/docs/overview.html) R application to Ploomber Cloud you need:

- A `Dockerfile`
- A `startApp.R` file (a script to start the App)
- An `install.R` file (a script to install dependencies)
- An `app.R` file (your Shiny code)

## Required files

You can use this [template](https://github.com/ploomber/doc/blob/main/examples/docker/shiny-r/shiny-r-data-visualization) to get started. The `Dockerfile` and `startApp.R` will remain the same, but you need to modify `install.R` and `app.R`.

In the `install.R` file, add all the dependencies that you need for your application to run. And put your application logic in the `app.R` file.


## Testing locally

To test your app, you can use `docker` locally:

```sh
# build the docker image
docker build . -t shiny-r

# run it
docker run -p 5000:80 shiny-r
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

Once you have all your files, create a zip file.

To deploy a Shiny app from the deployment menu, select the Docker option and follow the instructions:

![](../static/docker.png)