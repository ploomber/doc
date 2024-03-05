# Voilà

## Deploy an example

To download and deploy an example Voila application simply run:

```sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
ploomber-cloud examples voila/chat-with-csv
cd basic-app
ploomber-cloud init
ploomber-cloud deploy --watch
```

## Deploy your own app

To deploy a application you need two files:

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

To deploy a Voilà app from the deployment menu, follow these instructions:

![](../static/voila.png)