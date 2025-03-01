"""
Sample CLI (requires click, tested with click==8.1.3)
"""

import click


@click.group()
def cli():
    """Command-line interface"""
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
