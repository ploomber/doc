from invoke import task


@task
def build(c):
    """Build the documentation."""
    c.run("jupyter-book build doc")
