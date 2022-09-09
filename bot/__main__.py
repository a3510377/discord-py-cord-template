import os
import click
import logging

from typing import List

import dotenv


@click.command()
@click.option("-t", "input_token", help="input bot token", is_flag=True)
@click.option("-d", "--debug", "debug", help="debug output", is_flag=True)
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
def run(input_token: bool, debug: bool, token: str, level: List[str]):
    if input_token:
        token = click.prompt("Token", hide_input=True)
    elif not token:
        click.echo("Please enter a token")
        return
    # TODO: run bot


if __name__ == "__main__":
    dotenv.load_dotenv()
    run()
