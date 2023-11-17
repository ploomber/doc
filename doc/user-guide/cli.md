# Command-line interface

```{note}
Currently, Voila deployments are unsupported by the CLI. Environment variables and authentication are also unsupported. Expect support to be added soon.
```

You can deploy applications using the command-line interface. First, install the package:

```sh
pip install ploomber-cloud
```

Then, set your API key ([learn how to get it](../quickstart/apikey.md)):

```sh
ploomber-cloud key YOURKEY
```

## Initialize a new app

If you want to create a new app, run the `init` command:

```sh
ploomber-cloud init
```

This will prompt you for the project type (if this is a Docker-based project and you already have a `Dockerfile`, it'll ask you for confirmation).

Once the command exits, you can deploy:

```sh
ploomber-cloud deploy
```

The `deploy` command will print a URL that you can visit to track deployment progress.

## Configure an existing project

If you want to deploy an existing project, create a `ploomber-cloud.json` file in the root directory of your project with the following structure:

```json
{
    "id": "APP_ID",
    "type": "APP_TYPE"
}
```

Substitute `id` for your project ID and `type` for the app type (`docker`, `panel`, `streamlit`, etc.)

For example, if my app ID is `cool-tree-1860` and I'm deploying a `docker` app:


```json
{
    "id": "cool-tree-1860",
    "type": "docker"
}
```

Then, execute:


```sh
ploomber-cloud deploy
```

The `deploy` command will print a URL that you can visit to track deployment progress.