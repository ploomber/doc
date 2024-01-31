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

The `deploy` command will print a URL that you can visit to track deployment progress. If you would like to track progress in the command line,
add the `--watch` flag.

```sh
ploomber-cloud deploy --watch
```

## Configure an existing project

If you want to deploy an existing project run the `init` command with the `--from-existing` flag:

```sh
ploomber-cloud init --from-existing
```

This will prompt you to choose from a list of your existing projects.

Upon your choice, the command will generate a `ploomber-cloud.json` with your project's info. For example, if my app ID is `cool-tree-1860` and I'm deploying a `docker` app:


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

## Defining environment variables

If your project makes use of environment variables, you can define them in an `.env` file. Simply run:

```sh
touch .env
```

Then open `.env` in your code editor and enter your environment variables. It should look like this:

```
MY_ENV_VAR_1=value_1
MY_ENV_VAR_2=value_2
```

Now make sure your project has been initialized, and deploy it:

```sh
ploomber-cloud deploy
```

The command-line interface will automatically read your environment variables and include them in the deployment.

To learn how to read your environment variables from within your application, see [Reading variables.](./env-vars.md)