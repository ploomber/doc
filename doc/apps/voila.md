# Voilà

```{tip}
If you haven't deployed your first application, check out the [quickstart guide.](../quickstart/app.md)
```

To deploy a application you need two files:

1. A Jupyter notebook file (`.ipynb`)
2. A dependencies file (`requirements.txt`)

## Voilà

Currently, Ploomber Cloud supports `Voilà` for deploying Jupyter notebooks as applications. For information on how to write Voilà applications, [please check the documentation](https://voila.readthedocs.io/en/stable/).

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