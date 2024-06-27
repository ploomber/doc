---
myst:
  html_meta:
    description: Deploy a Chainlit app on Ploomber in seconds with this guide.
    keywords: chainlit, deployment, hosting
    property=og:title: Chainlit | Ploomber Docs
    property=og:description: Deploy a Chainlit app on Ploomber in seconds with this guide.
    property=og:image: https://docs.cloud.ploomber.io/en/latest/_static/opengraph-images-chainlit.png
    property=og:url: https://docs.cloud.ploomber.io/en/latest/apps/chainlit.html
---


# Chainlit

```{tip}
Ploomber Cloud is a great platform to host your Chainlit apps, even [Chainlit recommends us!](https://docs.chainlit.io/deployment/tutorials)
```

To deploy a Chainlit application in Ploomber Cloud you need:

- A [Ploomber Cloud](https://platform.ploomber.io/register?utm_source=flask&utm_medium=documentation) account
- Your application file (`app.py`)
- A dependencies file (`requirements.txt`)

## Testing locally

To test your app, you can use this command:

```sh
pip install -r requirements.txt
chainlit run app.py --host=0.0.0.0 --port=5000 --headless
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.

## Deploy

`````{tab-set}

````{tab-item} Web
__Deploy from the menu__

Once you have all your files, create a zip file.

To deploy a Chainlit app from the deployment menu, follow these instructions:

![](../static/chainlit.png)
````

````{tab-item} Command-line
__Try an example__

To download and deploy an example Chainlit application start by installing Ploomber Cloud and setting your API key:

```sh
pip install ploomber-cloud
ploomber-cloud key YOUR-KEY
```

```{tip}
If you don't have an API key yet, follow the [instructions here.](../quickstart/apikey.md)
```

Now, download an example. It will prompt you for a location to download the app. To download in the current directory, just press enter.

```sh
ploomber-cloud examples chainlit/basic-app
```

```{note}
A full list of Chainlit example apps is available [here.](https://github.com/ploomber/doc/tree/main/examples/chainlit)
```

You should see a confirmation with instructions on deploying your app. Now, navigate to your application:

```sh
cd location-you-entered/basic-app
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

Ploomber has features to help you deploy production-ready Chainlit apps

### Authentication

Our [integration with Auth0](auth0-integration) allows you to easily add authentication
to any Chainlit app. There's no need to modify your Chainlit app code, only pass your
Auth0 configuration parameters. Check out the [sample app.](https://github.com/ploomber/doc/tree/main/examples/chainlit/app-with-auth0)
In addition to the Auth0 parameters you also need to pass the `CHAINLIT_AUTH_SECRET` value. Refer to [this section](chainlit-password) to learn more.

## Features

Ploomber Cloud supports many features to help you build Streamlit applications quickly!

- Integration with [GitHub](../user-guide/github.md)
- Safely store [secrets](../user-guide/secrets.md) such as API keys
- Usage [analytics](../user-guide/analytics.md) such as unique visitors, total requests, etc.
- Spin up [larger resources](../user-guide/resources.md) (CPUs and RAM)
- Spin up [GPUs](../user-guide/gpu.md)
- Add custom [domains or subdomains](../user-guide/custom-domains.md) to your application
- [Task queues](task-queues) to scale applications to more users

(chainlit-password)=
## Password protection

Currently, our [password authentication](../user-guide/password.md) feature doesn't work with Chainlit, however,
we can still use Chainlit's authentication feature.

First, download the [sample code](https://github.com/ploomber/doc/tree/main/examples/chainlit/chainlit-with-password).
The `Dockerfile` remains the same, the only change happens in the `app.py`.

During deployment, you need to provide three [secrets](../user-guide/secrets.md):

```sh
CHAINTLIT_USERNAME="user"
CHAINTLIT_PASSWORD="somepassword"

CHAINLIT_AUTH_SECRET="somerandomstring"
```

`CHAINLIT_AUTH_SECRET` is a random string used to authenticate user tokens, you can
generate one by executing the following command in your terminal:

```sh
python -c 'from secrets import token_hex; print(token_hex(16))'
```

```{note}
You can change `CHAINLIT_AUTH_SECRET`, but it'll log out all your users.
```

## Troubleshooting

By default applications run with Python 3.11. Refer to this [section](../faq/faq.md#customize-deployment) for customized deployments.
[Here](https://github.com/ploomber/doc/tree/main/examples/chainlit/docker-based) is a sample Docker-based `Chainlit` application.

## Examples

::::{grid} 2 2 3 3
:class-container: text-center
:gutter: 2

:::{grid-item-card} Basic app
:link: https://github.com/ploomber/doc/tree/main/examples/chainlit/basic-app
![](https://github.com/ploomber/doc/raw/main/examples/chainlit/basic-app/screenshot.webp)
:::

:::{grid-item-card} App with password
:link: https://github.com/ploomber/doc/tree/main/examples/chainlit/chainlit-with-password
![](https://github.com/ploomber/doc/raw/main/examples/chainlit/chainlit-with-password/screenshot.webp)
:::

:::{grid-item-card} Chat with PDF
:link: https://github.com/ploomber/doc/tree/main/examples/chainlit/chat-with-pdf
![](https://github.com/ploomber/doc/raw/main/examples/chainlit/chat-with-pdf/screenshot.webp)
:::

:::{grid-item-card} Private ChatGPT
:link: https://github.com/ploomber/doc/tree/main/examples/chainlit/private-chatgpt
![](https://github.com/ploomber/doc/raw/main/examples/chainlit/private-chatgpt/screenshot.webp)
:::

:::{grid-item-card} App with custom CSS
:link: https://github.com/ploomber/doc/tree/main/examples/chainlit/app-with-custom-css
![](https://github.com/ploomber/doc/raw/main/examples/chainlit/app-with-custom-css/screenshot.webp)
:::


::::
