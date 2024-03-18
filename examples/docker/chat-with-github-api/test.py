import click
import requests

API_ROOT = "http://localhost:8000"

@click.group()
def cli():
    pass


@cli.command()
def index():
    response = requests.get(
            f"{API_ROOT}/",
            headers={
                "Content-Type": "application/json",
            },
        )

    return click.echo(response.content)


@cli.command()
@click.argument("owner")
@click.argument("name")
@click.argument("branch")
def scrape(owner, name, branch):
    response = requests.post(
            f"{API_ROOT}/scrape",
            headers={
                "Content-Type": "application/json",
            },
            json={"owner": owner, "name": name, "branch": branch}
        )

    return click.echo(response.content)


@cli.command()
@click.argument("repo_id")
def status(repo_id):
    response = requests.get(
            f"{API_ROOT}/status/{repo_id}",
            headers={
                "Content-Type": "application/json",
            },
        )

    return click.echo(response.content)


@cli.command()
@click.argument("repo_id")
@click.argument("q")
def ask(repo_id, q):
    response = requests.post(
            f"{API_ROOT}/ask",
            headers={
                "Content-Type": "application/json",
            },
            json={"repo_id": repo_id, "question": q}
        )

    return click.echo(response.content)


@cli.command()
def clear():
    response = requests.get(
            f"{API_ROOT}/clear",
            headers={
                "Content-Type": "application/json",
            },
        )

    return click.echo(response.content)


if __name__ == "__main__":
    cli()
