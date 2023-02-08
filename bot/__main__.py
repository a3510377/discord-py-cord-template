import os
import click
import logging

from typing import List

import dotenv


@click.command()
@click.option("-t", "input_token", help="input bot token", is_flag=True)
@click.option("-d", "--dev", "dev", help="dev mode", is_flag=True)
@click.option(
    "--token",
    "token",
    help="discord bot token",
    type=str,
    default=lambda: os.getenv("DISCORD_TOKEN"),
)
@click.option(
    "-l",
    "--level",
    "level",
    default="INFO",
    help="log level",
    type=click.Choice(logging._nameToLevel.keys(), case_sensitive=False),
)
def run(input_token: bool, dev: bool, token: str, level: List[str]):
    from .core.logging import init_logging
    from .core.bot import Bot

    if input_token:
        token = click.prompt("Token", hide_input=True)
    elif not token:
        click.echo("Please enter a token")
        click.echo("e.x. python -m bot --token <token>")
        click.echo(
            "token in https://discord.com/developers/applications "
            "> New Application > Create > Bot > Add Bot > Yes, do it!"
        )
        return

    init_logging(level=level)

    Bot(dev=dev).run(token)


if __name__ == "__main__":
    dotenv.load_dotenv()
    run()
