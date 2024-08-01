---
myst:
  html_meta:
    description: Deploy a Streamlit app on Ploomber in seconds with this guide.
    keywords: streamlit, deployment, hosting
    property=og:title: Streamlit | Ploomber Docs
    property=og:description: Deploy a Streamlit app on Ploomber in seconds with this guide.
    property=og:image: https://docs.cloud.ploomber.io/en/latest/_static/opengraph-images-streamlit.png
    property=og:url: https://docs.cloud.ploomber.io/en/latest/apps/streamlit.html
---

# Streamlit

Deploy a [Streamlit](https://streamlit.io/) app on Ploomber in seconds with this guide.

First, create an [account](https://platform.ploomber.io/register?utm_source=streamlit&utm_medium=documentation).

To deploy a Streamlit app you need at least two files:

1. Your application file (`app.py`)
2. A dependencies file (`requirements.txt`)

## Application file

Your `app.py` must be a Streamlit application. An example is available [here.](https://github.com/ploomber/doc/blob/main/examples/streamlit/data-viz/app.py)

## Dependencies

To deploy a new project, list your dependencies in a (`requirements.txt`). You must include the streamlit package. If you're using pandas and numpy together, your `requirements.txt` file will look like this:

```
# sample requirements.txt
streamlit
pandas
numpy
```

## Testing locally

To test your Streamlit app, create a virtual environment and install the packages:

```bash
pip install -r requirements.txt
```

Then run the following command to start the application:

```bash
streamlit run app.py
```

## Deploy

`````{tab-set}

````{tab-item} Web
__Deploy from the menu__

Once you have all your files, create a zip file.

To deploy a Streamlit app from the deployment menu, follow these instructions:

![](../static/streamlit.png)
````

````{tab-item} Command-line
__Try an example__

To download and deploy an example Streamlit application start by installing Ploomber Cloud and setting your API key:

```sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
```

```{tip}
If you don't have an API key yet, follow the [instructions here.](../quickstart/apikey.md)
```

Now, download an example. It will prompt you for a location to download the app. To download in the current directory, just press enter.

```sh
ploomber-cloud examples streamlit/data-viz
```

```{note}
A full list of Streamlit example apps is available [here.](https://github.com/ploomber/doc/tree/main/examples/streamlit)
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

## Production deployments

Ploomber has features to help you deploy production-ready Streamlit apps

### Authentication

Our [integration with Auth0](auth0-integration) allows you to easily add authentication
to any Streamlit app. There's no need to modify your Streamlit app code, only pass your
Auth0 configuration parameters. Check out the [sample app.](https://github.com/ploomber/doc/tree/main/examples/streamlit/app-with-auth0)

![auth0-login](../static/password/auth0-login.png)

## Connecting to a DB

You can use the [st.connection](https://docs.streamlit.io/develop/api-reference/connections/st.connection) API for connecting to a database from a Streamlit app.
Check out this [sample app](https://github.com/ploomber/doc/tree/main/examples/streamlit/db-connection) that demonstrates DB connection.

You can set the SQLAlchemy URI of your DB as an environment variable `DB_URI` and pass it using the `url` argument:

```python
import streamlit as st
from os import environ

conn = st.connection(name="db_connection",
                     type='sql',
                     url=environ["DB_URI"])
```

You can pass any relevant value as the `name` argument. When deploying on Ploomber Cloud the `DB_URI` value needs to be set as a [secret](https://docs.cloud.ploomber.io/en/latest/user-guide/secrets.html):

![](../static/streamlit_db.png)

Note that the database URI is a SQLAlchemy URI and should have the format:

```python
dialect://username:password@host:port/database
```

Here's an example of a `Postgres` connection URI:

```python
postgresql://scott:tiger@localhost:5432/mydatabase
```

To learn more about the URI format refer to the [documentation](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls).

## Other features

Ploomber Cloud supports many features to help you build Streamlit applications quickly!

- Integration with [GitHub](../user-guide/github.md)
- Safely store [secrets](../user-guide/secrets.md) such as API keys
- Usage [analytics](../user-guide/analytics.md) such as unique visitors, total requests, etc.
- Spin up [larger resources](../user-guide/resources.md) (CPUs and RAM)
- Spin up [GPUs](../user-guide/gpu.md)
- Add custom [domains or subdomains](../user-guide/custom-domains.md) to your application
- [Task queues](task-queues) to scale applications to more users


## Troubleshooting

By default applications run with Python 3.11. Refer to this [section](../faq/faq.md#customize-deployment) for customized deployments.
[Here](https://github.com/ploomber/doc/tree/main/examples/streamlit/docker-based) is a sample Docker-based `Streamlit` application.

## Examples

::::{grid} 2 2 3 3
:class-container: text-center
:gutter: 2

:::{grid-item-card} Basic app
:link: https://github.com/ploomber/doc/tree/main/examples/streamlit/basic-app
:::

:::{grid-item-card} Data visualization
:link: https://github.com/ploomber/doc/tree/main/examples/streamlit/data-viz
![](https://github.com/ploomber/doc/raw/main/examples/streamlit/data-viz/screenshot.webp)
:::

:::{grid-item-card} Mirascope URL extractor
:link: https://github.com/ploomber/doc/tree/main/examples/streamlit/mirascope-url-extractor
![](https://github.com/ploomber/doc/raw/main/examples/streamlit/mirascope-url-extractor/screenshot.png)
:::
:::

:::{grid-item-card} Iris Dashboard Using PostgreSQL
<!-- :link: https://github.com/ploomber/doc/tree/main/examples/streamlit/postgres-connection
![](https://github.com/ploomber/doc/raw/main/examples/streamlit/postgres-connection/app.png) -->
:::

::::
