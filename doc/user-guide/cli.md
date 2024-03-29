# Command-line interface

You can deploy applications using the command-line interface. First, install the package:

```sh
pip install ploomber-cloud
```

Then, set your API key ([learn how to get it](../quickstart/apikey.md)):

```sh
ploomber-cloud key YOURKEY
```

```{tip}
`pc` is a shortcut for `ploomber-cloud`. Example: `pc key`
```

(init)=
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

## Deploying an example

Ploomber Cloud hosts example applications for many different frameworks. To download and deploy one, run `ploomber-cloud examples`:

```sh
ploomber-cloud examples
```

Follow the prompts to choose a framework and specific example name. You may also specify a directory in which to download the example.

Once the application is downloaded, it's ready to deploy! For example, if you downloaded the `basic-app` example for `Flask` in the current directory:

```sh
ploomber-cloud key YOUR-KEY
cd basic-app
ploomber-cloud init
ploomber-cloud deploy --watch
```

If you already know which example you want, you can download it while avoiding prompts with `ploomber-cloud examples framework/example-name`:

```sh
ploomber-cloud examples flask/basic-app
```

A full list of example applications is available [here](https://github.com/bryannho/doc/tree/main/examples)

## Defining secrets

If your project uses secrets, you can define them in an `.env` file.

In your main project directory, create an `.env` file. Open it in your code editor, and enter your secrets. It should look like this:

```
MY_SECRET_1=value_1
MY_SECRET_2=value_2
```

Now make sure your project has been [initialized](init), and deploy it:

```sh
ploomber-cloud deploy
```

The command-line interface will automatically read and encrypt your secrets and include them in the deployment.
For security reasons, your `.env` file is replaced with an empty file at runtime. Ploomber only stores your encrypted secrets.

To learn how to read your secrets from within your application, see [Reading secrets.](./secrets.md)