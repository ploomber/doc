# Voilà

## Voila applications

To deploy an application you need two files:

1. A Jupyter notebook file (`.ipynb`)
2. A dependencies file (`requirements.txt`)

For information on how to write Voilà applications, [please check the documentation](https://voila.readthedocs.io/en/stable/).

Click here to see [some examples.](../examples/voila.md)

## Dependencies

To deploy a new project, list your dependencies in a (`requirements.txt`). For example, if you're using [JupySQL](https://jupysql.ploomber.io), pandas and matplotlib, your `requirements.txt` file will look like this:

```
# sample requirements.txt
jupysql
pandas
matplotlib
```

## Deploy

````{tab-set}

```{tab-item} UI
### Deploy from the menu

To deploy a Voilà app from the deployment menu, follow these instructions:

![](../static/voila.png)
```

```{tab-item} CLI
### Try an example

To download and deploy an example Voila application start by installing Ploomber Cloud and setting your API key:

``sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
``

``{tip}
To get an API key, follow [these instructions.](../quickstart/apikey.md)
``

Now, download an example. It will prompt you for a location to download the app. To download in the current directory, just press enter.

``sh
ploomber-cloud examples voila/chat-with-csv
``

You should see a confirmation with instructions on deploying your app. Now, navigate to your application:

``sh
cd location-you-entered/chat-with-csv
``

### Deploy from the CLI

``sh
ploomber-cloud init
ploomber-cloud deploy --watch
``

```
````