import os
import click
import logging

from typing import List, Union

import dotenv


@click.command()
@click.option("-t", "input_token", help="input bot token", is_flag=True)
@click.option("-d", "--dev", "dev", help="dev mode", is_flag=True)
@click.option(
    "--token",
    "token",
    help="discord bot token",
    type=str,
)
@click.option(
    "-l",
    "--level",
    "level",
    default="INFO",
    help="log level",
    type=click.Choice(logging._nameToLevel.keys(), case_sensitive=False),
)
@click.option(
    "-e",
    "--from-env",
    "env_path",
    default=True,
    help="load env file path or stop load env file",
)
def run(
    input_token: bool,
    dev: bool,
    token: str,
    level: List[str],
    env_path: Union[str, bool],
):
    from .core.logging import init_logging
    from .core.bot import Bot

    if env_path is not None:
        if isinstance(env_path, str):
            dotenv.load_dotenv(env_path)
        elif env_path:
            dotenv.load_dotenv()

    token = os.getenv("DISCORD_TOKEN")

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
    run()
