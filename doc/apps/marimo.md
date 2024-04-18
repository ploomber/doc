---
myst:
  html_meta:
    description: Deploy Marimo on Ploomber in seconds with this guide.
    keywords: marimo, notebooks, hosting
    property=og:title: Marimo | Ploomber Docs
    property=og:description: Deploy Marimo on Ploomber in seconds with this guide.
    property=og:image: https://docs.cloud.ploomber.io/en/latest/_static/opengraph-images-marimo.png
    property=og:url: https://docs.cloud.ploomber.io/en/latest/apps/marimo.html
---


# Marimo

To deploy a [Marimo](https://github.com/marimo-team/marimo) on Ploomber Cloud you need:

- A [Ploomber Cloud](https://platform.ploomber.io/register?utm_source=flask&utm_medium=documentation) account
- Deployment files



```{important}
If you're on a free account, back up your work because your app can be terminated if inactive. If you need Marimo deployed with production settings, contact us [contact@ploomber.io](mailto:contact.ploomber.io)
```

`````{tab-set}

````{tab-item} Web
__Deploy from the menu__

You can deploy Marimo to Ploomber Cloud and use it as a development environment. First, create an [account](https://platform.ploomber.io/register?utm_source=marimo&utm_medium=documentation).

Then, download the files from the
[example](https://github.com/ploomber/doc/tree/main/examples/docker/marimo), create a `.zip` file and deploy it using the Docker option:

![](../static/docker.png)
````

````{tab-item} Command-line

To download and deploy Marimo start by installing Ploomber Cloud and setting your API key:

```sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
```

```{tip}
If you don't have an API key yet, follow the [instructions here.](../quickstart/apikey.md)
```

Now, download the Marimo example. It will prompt you for a location to download the app. To download in the current directory, just press enter.

```sh
ploomber-cloud examples docker/marimo
```

You should see a confirmation with instructions on deploying your app. Now, navigate to your application:

```sh
# this is the default location
cd marimo/
```

__Deploy from the CLI__

Initialize and deploy your app with:

```sh
ploomber-cloud init
ploomber-cloud deploy
```

You can view the deployed application by logging in to your Ploomber Cloud account.

````
`````