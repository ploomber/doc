"""
Sample CLI (requires click, tested with click==8.1.3)
"""

import sys

import click


class AliasedGroup(click.Group):
    """
    Allow running commands by only typing the first few characters.
    https://click.palletsprojects.com/en/8.1.x/advanced/#command-aliases

    To disable, remove the `cls=AliasedGroup` argument from the `@click.group()` decorator.
    """

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args


# NOTE: this requires ipdb
def pdb_option(f):
    """Decorator to add --pdb option to any command."""

    def callback(ctx, param, value):
        if value:

            def excepthook(type_, value, traceback):
                import ipdb

                ipdb.post_mortem(traceback)

            sys.excepthook = excepthook

    return click.option(
        "--pdb", is_flag=True, help="Drop into pdb on exceptions", callback=callback
    )(f)


@click.group(cls=AliasedGroup)
def cli():
    pass


@cli.command()
@pdb_option
def test(pdb: bool):  # NOTE: you must add pdb as an argument
    """Test command for the pdb option"""
    x = 1
    y = 0
    print(x / y)


@cli.command()
@click.argument("name")
def hello(name):
    """Say hello to someone"""
    print(f"Hello, {name}!")


@cli.command()
@click.argument("name")
def log(name):
    """Log a message"""
    from mcp_ploomber.log import configure_file_and_print_logger, get_logger

    configure_file_and_print_logger()
    logger = get_logger()
    logger.info(f"Hello, {name}!", name=name)


if __name__ == "__main__":
    cli()
