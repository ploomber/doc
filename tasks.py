from invoke import task


@task
def setup(c, version=None):
    """
    Setup dev environment, requires conda
    """
    env_name = f"cloud-doc"
    c.run(f"conda env create --file environment.yml --name {env_name}")
    print(f"Done! Activate your environment with:\nconda activate {env_name}")


@task
def build(c):
    """Build the documentation."""
    c.run("jupyter-book build doc")
