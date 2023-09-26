# Voilà

```{tip}
If you haven't deployed your first dashboard, check out the [quickstart guide.](../quickstart/app.md)
```

To deploy a dashboard you need two files:

1. A Jupyter notebook file (`.ipynb`)
2. A dependencies file (`requirements.txt`)

## Voilà

Currently, Ploomber Cloud supports [Voilà](https://voila.readthedocs.io/en/stable/) for deploying Jupyter notebooks as dashboards. For information on how to write Voilà dashboards, [please check the documentation](https://voila.readthedocs.io/en/stable/).

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