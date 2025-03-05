"""
Sample CLI (requires click, tested with click==8.1.3)
"""

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


@click.group(cls=AliasedGroup)
def cli():
    pass


@cli.command()
@click.argument("name")
def hello(name):
    """Say hello to someone"""
    print(f"Hello, {name}!")


@cli.command()
@click.argument("name")
def log(name):
    """Log a message"""
    # flake8: noqa
    from $package_name.log import configure_file_and_print_logger, get_logger

    configure_file_and_print_logger()
    logger = get_logger()
    logger.info(f"Hello, {name}!", name=name)


if __name__ == "__main__":
    cli()
