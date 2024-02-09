# Quarto

You can deploy [Quarto](https://quarto.org/) projects to Ploomber Cloud. We currently
support the following types of projects: website, blog, manuscript, and confluence.

Let's create a new website and put it under `myproject/` (you can use an existing project as well):

```sh
quarto create project website myproject --no-open
```

The next step depends on whether you want to render files locally (i.e. run
`quarto render`) or you want Ploomber Cloud to render your files. In the latter case,
you don't even need to install `quarto` locally!


## Render files locally

```{note}
A full sample project is available [here](https://github.com/ploomber/doc/tree/main/examples/quarto/quarto-website)
```

Create a `Dockerfile` with the following contents:

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

### Test locally

To test locally, you can run the following command:

```
python -m http.server 5000 --directory myproject/_site/
```

Then, open `http://localhost:5000`

If your project looks well, you are ready to deploy it!

## Render files remotely

```{note}
A full sample project is available [here](https://github.com/ploomber/doc/tree/main/examples/quarto/quarto-remote-render)
```

In this case, the `Dockerfile` is slightly different:

```Dockerfile
FROM python:3.11

RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb
RUN apt-get update
RUN apt-get install gdebi-core -y
RUN gdebi quarto-linux-amd64.deb --non-interactive

# update this if your project is in a directory with a different name!
COPY myproject/ myproject/
RUN quarto render myproject

ENTRYPOINT ["python", "-m", "http.server", "80", "--bind", "0.0.0.0", "--directory", "myproject/_site"]
```

It's a bit longer since it needs to install Quarto and render your files.

Put your source files next to the `Dockerfile`:

```
.
├── Dockerfile
├── README.md
└── myproject
    ├── _quarto.yml
    ├── about.qmd
    ├── index.qmd
    └── styles.css

1 directory, 6 files
```

## Deploy

```{tip}
You can add password protection to your Quarto project, click here to [learn more.](../user-guide/password.md)
```

To deploy the app from the deployment menu, zip everything (the `Dockerfile` and
the `myproject/` directory) and follow these instructions:

![](../static/docker.png)