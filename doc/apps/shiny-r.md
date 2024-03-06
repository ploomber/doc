# Shiny (R)

To deploy a [Shiny](https://shiny.posit.co/py/docs/overview.html) R application to Ploomber Cloud you need:

- A `startApp.R` file (a script to start the App)
- An `install.R` file (a script to install dependencies)
- An `app.R` file (your Shiny code)

## Required files

You can use this [template](https://github.com/ploomber/doc/blob/main/examples/shiny-r/shiny-r-data-visualization) to get started. The `startApp.R` will remain the same, but you need to modify `install.R` and `app.R`.

In the `install.R` file, add all the dependencies that you need for your application to run. And put your application logic in the `app.R` file.


## Testing locally

To test your Shiny app, you can run the following commands locally:

```sh
# Install dependencies
Rscript install.R

# Start the application
Rscript startApp.R
```

## Deploy

`````{tab-set}

````{tab-item} Web
__Deploy from the menu__

Once you have all your files, create a zip file.

To deploy a Shiny app from the deployment menu, select the Shiny (R) option and follow the instructions:

![](../static/shiny-r.png)
````

````{tab-item} Command-line
__Try an example__

To download and deploy an example Shiny-R application start by installing Ploomber Cloud and setting your API key:

```sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
```

```{tip}
If you don't have an API key yet, follow the [instructions here.](../quickstart/apikey.md)
```

Now, download an example. It will prompt you for a location to download the app. To download in the current directory, just press enter.

```sh
ploomber-cloud examples shiny-r/shiny-r-data-visualization
```

```{note}
A full list of Solara example apps is available [here.](https://github.com/ploomber/doc/tree/main/examples/shiny-r)
```

You should see a confirmation with instructions on deploying your app. Now, navigate to your application:

```sh
cd location-you-entered/shiny-r-data-visualization
```

__Deploy from the CLI__

Initialize and deploy your app with:

```sh
ploomber-cloud init
ploomber-cloud deploy --watch
```

````
`````