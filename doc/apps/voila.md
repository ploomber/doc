---
myst:
  html_meta:
    description: Deploy a Voilà app on Ploomber in seconds with this guide.
    keywords: voila, deployment, hosting
    property=og:title: Voilà | Ploomber Docs
    property=og:description: Deploy a Voilà app on Ploomber in seconds with this guide.
    property=og:image: https://docs.cloud.ploomber.io/en/latest/_static/opengraph-images-voila.png
    property=og:url: https://docs.cloud.ploomber.io/en/latest/apps/voila.html
---

# Voilà

To deploy an app first create an [account](https://platform.ploomber.io/register?utm_source=voila&utm_medium=documentation).


## Voila applications

To deploy an application you need two files:

1. A Jupyter notebook file (`.ipynb`)
2. A dependencies file (`requirements.txt`)

For information on how to write Voilà applications, [please check the documentation](https://voila.readthedocs.io/en/stable/).

## Dependencies

To deploy a new project, list your dependencies in a (`requirements.txt`). For example, if you're using [JupySQL](https://jupysql.ploomber.io), pandas and matplotlib, your `requirements.txt` file will look like this:

```
# sample requirements.txt
jupysql
pandas
matplotlib
```

## Deploy

`````{tab-set}

````{tab-item} Web
__Deploy from the menu__

Once you have all your files, create a zip file.

To deploy a Voilà app from the deployment menu, follow these instructions:

![](../static/voila.png)
````

````{tab-item} Command-line
__Try an example__

To download and deploy an example Voila application start by installing Ploomber Cloud and setting your API key:

```sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
```

```{tip}
If you don't have an API key yet, follow the [instructions here.](../quickstart/apikey.md)
```

Now, download an example. It will prompt you for a location to download the app. To download in the current directory, just press enter.

```sh
ploomber-cloud examples voila/chat-with-csv
```

You should see a confirmation with instructions on deploying your app. Now, navigate to your application:

```sh
cd location-you-entered/chat-with-csv
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

## Production deployments

Ploomber has features to help you deploy production-ready Voila apps

### Authentication

Our [integration with Auth0](auth0-integration) allows you to easily add authentication
to any Voila app. There's no need to modify your Voila app code, only pass your
Auth0 configuration parameters. Check out the [sample app.](https://github.com/ploomber/doc/tree/main/examples/voila/app-with-auth0)

## Features

Ploomber Cloud supports many features to help you build Voilà applications quickly!

- Integration with [GitHub](../user-guide/github.md)
- Safely store [secrets](../user-guide/secrets.md) such as API keys
- Usage [analytics](../user-guide/analytics.md) such as unique visitors, total requests, etc.
- Spin up [larger resources](../user-guide/resources.md) (CPUs and RAM)
- Spin up [GPUs](../user-guide/gpu.md)
- Add custom [domains or subdomains](../user-guide/custom-domains.md) to your application
- [Task queues](task-queues) to scale applications to more users


## Troubleshooting

By default applications run with Python 3.11. Refer to this [section](../faq/faq.md#customize-deployment) for customized deployments.
[Here](https://github.com/ploomber/doc/tree/main/examples/voila/docker-based) is a sample Docker-based `Voila` application.

## Examples

::::{grid} 2 2 3 3
:class-container: text-center
:gutter: 2

:::{grid-item-card} Animated visualization
:link: https://github.com/ploomber/doc/tree/main/examples/voila/animated-viz
![](https://github.com/ploomber/doc/raw/main/examples/voila/animated-viz/screenshot.webp)
:::

:::{grid-item-card} Chat with CSV
:link: https://github.com/ploomber/doc/tree/main/examples/voila/chat-with-csv
![](https://github.com/ploomber/doc/raw/main/examples/voila/chat-with-csv/screenshot.webp)
:::

:::{grid-item-card} GDAL + geopandas
:link: https://github.com/ploomber/doc/tree/main/examples/voila/gdal
![](https://github.com/ploomber/doc/raw/main/examples/voila/gdal/screenshot.webp)
:::

:::{grid-item-card} Image mask generator
:link: https://github.com/ploomber/doc/tree/main/examples/voila/image-mask-generator
![](https://github.com/ploomber/doc/raw/main/examples/voila/image-mask-generator/screenshot.webp)
:::

:::{grid-item-card} ML predictions
:link: https://github.com/ploomber/doc/tree/main/examples/voila/ml
![](https://github.com/ploomber/doc/raw/main/examples/voila/ml/screenshot.webp)
:::


:::{grid-item-card} Interactive data viz
:link: https://github.com/ploomber/doc/tree/main/examples/voila/mosaic
![](https://github.com/ploomber/doc/raw/main/examples/voila/mosaic/screenshot.webp)
:::

:::{grid-item-card} Object removal
:link: https://github.com/ploomber/doc/tree/main/examples/voila/object-removal
![](https://github.com/ploomber/doc/raw/main/examples/voila/object-removal/screenshot.webp)
:::


::::
