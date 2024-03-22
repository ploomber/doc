# Panel

```{eval-rst}
.. meta::
   :description: Deploy Panel apps for free
   :keywords: panel, holoviews, deployment, hosting
   :author: Ploomber
```

Ploomber Cloud supports [Panel](https://github.com/holoviz/panel). For information on how to develop Panel apps, [please check the documentation](https://panel.holoviz.org/).

To deploy an app, first create an [account](https://platform.ploomber.io/register?utm_source=panel&utm_medium=documentation).

Once you have an account, you need at least two files:

1. Your application file (`app.py`)
2. A dependencies file (`requirements.txt`)

## Application file

Your `app.py` must be a Panel application. An example is available [here.](https://github.com/ploomber/doc/blob/main/examples/panel/data-viz/app.py)

## Dependencies

To deploy a new project, list your dependencies in a (`requirements.txt`). For example, if you're using [JupySQL](https://jupysql.ploomber.io), pandas and matplotlib, your `requirements.txt` file will look like this:

```
# sample requirements.txt
jupysql
pandas
matplotlib
```

## Testing locally

To test your Panel app, create a virtual environment and install the packages:

```bash
pip install -r requirements.txt
```

Then run the following command to start the application:

```bash
panel serve app.py
```

## Deploy

`````{tab-set}

````{tab-item} Web
__Deploy from the menu__

Once you have all your files, create a zip file.

To deploy a Panel app from the deployment menu, follow these instructions:

![](../static/panel.png)

To learn more about deploying Panel applications on Ploomber Cloud [click here](https://panel.holoviz.org/how_to/deployment/ploomber.html)
````

````{tab-item} Command-line
__Try an example__

To download and deploy an example Panel application start by installing Ploomber Cloud and setting your API key:

```sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
```

```{tip}
If you don't have an API key yet, follow the [instructions here.](../quickstart/apikey.md)
```

Now, download an example. It will prompt you for a location to download the app. To download in the current directory, just press enter.

```sh
ploomber-cloud examples panel/data-viz
```

```{note}
A full list of Panel example apps is available [here.](https://github.com/ploomber/doc/tree/main/examples/panel)
```

You should see a confirmation with instructions on deploying your app. Now, navigate to your application:

```sh
cd location-you-entered/data-viz
```

__Deploy from the CLI__

Initialize and deploy your app with:

```sh
ploomber-cloud init
ploomber-cloud deploy --watch
```

````
`````


```{tip}
To ensure your app doesn't break on re-deployments, pin your [dependencies.](pin-dependencies)
```