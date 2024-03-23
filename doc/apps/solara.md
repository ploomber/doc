---
myst:
  html_meta:
    description: Deploy a Solara app on Ploomber in seconds with this guide.
    keywords: solara, deployment, hosting
    property=og:title: Solara | Ploomber Docs
    property=og:description: Deploy a Solara app on Ploomber in seconds with this guide.
    property=og:image: https://docs.cloud.ploomber.io/en/latest/_static/opengraph-images-solara.png
    property=og:url: https://docs.cloud.ploomber.io/en/latest/apps/solara.html
---


# Solara

Ploomber Cloud supports [Solara](https://solara.dev/). For information on how to develop Solara apps, [please check the documentation](https://solara.dev/docs).

First, create an [account](https://platform.ploomber.io/register?utm_source=solara&utm_medium=documentation).

To deploy a Solara app you need at least two files zipped up:

1. Your application file (`app.py`)
2. A dependencies file (`requirements.txt`)

```{note}
We currently only support Solara deployments via a `app.py` file, not via `.ipynb` files
```

## Dependencies

To deploy a new project, list your dependencies in a (`requirements.txt`). For example, if you're using [JupySQL](https://jupysql.ploomber.io), pandas and matplotlib in the solara application, your `requirements.txt` file will look like this:

```
# sample requirements.txt
solara
jupysql
pandas
matplotlib
```

## Testing locally

To test your Solara app, create a virtual environment and install the packages:

```bash
pip install -r requirements.txt
```

Then run the following command to start the application:

```bash
solara run app.py
```

## Deploy

`````{tab-set}

````{tab-item} Web
__Deploy from the menu__

Once you have all your files, create a zip file.

To deploy a Solara app from the deployment menu, follow these instructions:

![](../static/solara.png)
````

````{tab-item} Command-line
__Try an example__

To download and deploy an example Solara application start by installing Ploomber Cloud and setting your API key:

```sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
```

```{tip}
If you don't have an API key yet, follow the [instructions here.](../quickstart/apikey.md)
```

Now, download an example. It will prompt you for a location to download the app. To download in the current directory, just press enter.

```sh
ploomber-cloud examples solara/gpt-4-tokenizer
```

```{note}
A full list of Solara example apps is available [here.](https://github.com/ploomber/doc/tree/main/examples/solara)
```

You should see a confirmation with instructions on deploying your app. Now, navigate to your application:

```sh
cd location-you-entered/gpt-4-tokenizer
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

## Examples

::::{grid} 2 2 3 3
:class-container: text-center
:gutter: 2


:::{grid-item-card} Arxiv chat
:link: https://github.com/ploomber/doc/tree/main/examples/solara/arxiv-chat
![](https://github.com/ploomber/doc/raw/main/examples/solara/arxiv-chat/screenshot.webp)
:::

:::{grid-item-card} Chat with CSV
:link: https://github.com/ploomber/doc/tree/main/examples/solara/chat-with-csv
![](https://github.com/ploomber/doc/raw/main/examples/solara/chat-with-csv/screenshot.webp)
:::

:::{grid-item-card} Describe image
:link: https://github.com/ploomber/doc/tree/main/examples/solara/describe-image-frontend
![](https://github.com/ploomber/doc/raw/main/examples/solara/describe-image-frontend/screenshot.webp)
:::

:::{grid-item-card} Keyword extraction
:link: https://github.com/ploomber/doc/tree/main/examples/solara/keyword-extraction
![](https://github.com/ploomber/doc/raw/main/examples/solara/keyword-extraction/screenshot.webp)
:::

:::{grid-item-card} OCR
:link: https://github.com/ploomber/doc/tree/main/examples/solara/ocr
![](https://github.com/ploomber/doc/raw/main/examples/solara/ocr/screenshot.webp)
:::


::::
