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

Once you have all your files, create a zip file.

To deploy a Shiny app from the deployment menu, select the Shiny (R) option and follow the instructions:

![](../static/shiny-r.png)
