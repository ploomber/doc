# GitHub deployment

You can use GitHub Actions to deploy your project on each push.

## Set Github secret

First, you need to get your [API key](../quickstart/apikey.md). Once you have the API
key, you need to store it as a GitHub secret in your repository:

![](../static/github/add-secret.png)

![](../static/github/set-secret.png)


## Initialize project

Then, install the CLI:

```sh
# install package
pip install ploomber-cloud
```

And set the API key locally:

```sh
ploomber-cloud key YOURKEY
```

Now, configure your project:

```sh
ploomber-cloud init
```

`init` will create a `ploomber-cloud.json` file. For more information on the `init` command, see [](../user-guide/cli.md)

(monitor)=
## Configure and monitor Github actions

Now, configure GitHub actions by adding [this YAML file](https://github.com/edublancas/cloud-template/blob/main/.github/workflows/ploomber-cloud.yaml) in `.github/workflows/ploomber-cloud.yaml`

Finally, commit and push the new files:

```sh
# commit ploomber cloud and github actions config files
git add ploomber-cloud.json .github/workflows/ploomber-cloud.yaml
git commit -m 'configure github actions deployment'
git push
```

Once you push, you can monitor progress from GitHub. First, go to the actions section:

![](../static/github/see-actions.png)

Then, click on the most recent run, and you'll see the logs:

![](../static/github/logs-watch.png)

In the logs, you will see updates on the progress of the deployment. You'll also see a URL to your project dashboard where you can check its status.
Once the deployment has succeeded, it will return a URL to view your deployed project.

If you would prefer to track progress only through the project dashboard, you can remove `--watch` from the `deploy` command in your `ploomber-cloud.yaml`:

```yaml
 - name: Deploy
        env:
          PLOOMBER_CLOUD_KEY: ${{ secrets.PLOOMBER_CLOUD_KEY }}
        run: |
          ploomber-cloud deploy # removed '--watch' here
```

Removing `--watch` means deployment updates won't be output to the logs, but you will still be able to track its progress through the URL.

Without `--watch`, the logs will look like this:

![](../static/github/logs.png)

A complete sample project is [available here.](https://github.com/edublancas/cloud-template)

## Configure action through CLI

If your project is already hosted on Github, running `ploomber-cloud init` inside your repository folder will initialize
the project and prompt for configuring Github action:

```bash
Your app 'snowy-disk-4284' has been configured successfully!
Do you want to configure a github action? [y/N]: 
```

On confirming with `y` the CLI will create a `ploomber-cloud.yaml` file in the path `.github/workflows`.
In order to trigger an action for deploying the project using Github actions you need to add, commit and push this file along with the `ploomber-cloud.json`.

Once done, you can monitor progress as discussed [above](monitor). Ensure that the API key is set as Github secret.

In case the [workflow template](https://github.com/edublancas/cloud-template/blob/main/.github/workflows/ploomber-cloud.yaml) has been updated, and you need to re-initialise the application the CLI will prompt your for updating the workflow file:

```bash
Your app 'red-river-8187' has been configured successfully!
.github/workflows/ploomber-cloud.yaml seems outdated. Do you want to configure a github action? [y/N]:
```

Please review the workflow file and update if needed.