# Dash

To deploy a [Dash](https://dash.plotly.com/) application to Ploomber Cloud you need at least two files zipped up:

1. Your application file (`app.py`)
2. A dependencies file (`requirements.txt`)

## Required files

You can use this [template](https://github.com/ploomber/doc/blob/main/examples/dash) to get started. 

In the `requirements.txt` file, add all the dependencies that you need for your application to run. The application logic should exist in an `app.py` file and be initialized in this way:

```python
# name your app "app"
app = Dash(__name__)
# add this line below
server = app.server
```

## Testing locally

To test the Dash application, you can run the following commands locally:

```sh
# build the docker image
pip install -r requirements.txt

# Start the dash application
gunicorn app:server run --bind 0.0.0.0:5000
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.

## Deploy

`````{tab-set}

````{tab-item} Web
__Deploy from the menu__

Once you have all your files, create a zip file.

To deploy a Dash app from the deployment menu, select the Dash option and follow the instructions:

![](../static/dash.png)
````

````{tab-item} Command-line
__Try an example__

To download and deploy an example Dash application start by installing Ploomber Cloud and setting your API key:

```sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
```

```{tip}
If you don't have an API key yet, follow the [instructions here.](../quickstart/apikey.md)
```

Now, download an example. It will prompt you for a location to download the app. To download in the current directory, just press enter.

```sh
ploomber-cloud examples dash/clinical-analytics
```

```{note}
A full list of Dash example apps is available [here.](https://github.com/ploomber/doc/tree/main/examples/dash)
```

You should see a confirmation with instructions on deploying your app. Now, navigate to your application:

```sh
cd location-you-entered/clinical-analytics
```

__Deploy from the CLI__

Initialize and deploy your app with:

```sh
ploomber-cloud init
ploomber-cloud deploy --watch
```

````
`````