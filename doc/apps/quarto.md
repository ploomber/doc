# Quarto

You can deploy [Quarto](https://quarto.org/) projects to Ploomber Cloud.

We currently support the following types of projects: website, blog, manuscript, and confluence.

Let's create a new website and put it under `myproject/` (you can use an existing project as well):

```sh
quarto create project website myproject --no-open
```

Now, create a `Dockerfile` with the following contents:

```Dockerfile
FROM python:3.11

# update this if your project is in a directory with a different name!
COPY myproject/_site/ _site/
ENTRYPOINT ["python", "-m", "http.server", "80", "--bind", "0.0.0.0", "--directory", "_site"]
```

You project should look like this:

```
.
├── Dockerfile
└── myproject
    ├── _quarto.yml
    ├── about.qmd
    ├── index.qmd
    └── styles.css

1 directory, 5 files
```

As you can see, we have our `Dockerfile` and our project in the `myproject/` directory.

Now, let's render our project:

```sh
quarto render myproject
```

The previous commnad should print: `Output created: _site/index.html`

Now, your project should look like this:

```
├── Dockerfile
└── myproject
    ├── _quarto.yml
    ├── _site
    │   ├── about.html
    │   ├── index.html
    │   ├── search.json
    │   ├── site_libs
    │   └── styles.css
    ├── about.qmd
    ├── index.qmd
    └── styles.css
```

## Test locally

To test locally, you can run the following command:

```
python -m http.server 5000 --directory myproject/_site/
```

Then, open `http://localhost:5000`

If your project looks well, you are ready to deploy it!


## Deploy

```{tip}
You can add password protection to your Quarto project, click here to [learn more.](../user-guide/password.md)
```

To deploy the app from the deployment menu, zip everything (the `Dockerfile` and
the `myproject/` directory) and follow these instructions:

![](../static/docker.png)