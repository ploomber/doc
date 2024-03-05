# Panel

Ploomber Cloud supports [Panel](https://github.com/holoviz/panel). For information on how to develop Panel apps, [please check the documentation](https://panel.holoviz.org/).

To deploy a Panel app you need at least two files:

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

To test your Panel app, you can run the following command locally:

```bash
panel serve app.py
```

## Deploy

To deploy a Panel app from the deployment menu, follow these instructions:

![](../static/panel.png)

To learn more about deploying Panel applications on Ploomber Cloud [click here](https://panel.holoviz.org/how_to/deployment/ploomber.html)