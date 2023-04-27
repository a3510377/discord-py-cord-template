import logging
import os
from pathlib import Path
from typing import List, Union

import click
import dotenv
from discord.commands.core import valid_locales


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
@click.option(
    "-s",
    "--summon-i18n-file",
    "summon_i18n",
    is_flag=True,
    help="summon i18n file",
)
@click.option("-l", "lang", help="summon_i18n output langs", default="zh-TW", type=str)
@click.option(
    "-f",
    "arg_include_paths",
    help="include paths",
    multiple=True,
    type=Path,
)
@click.option("-r", "recursive", help="use recursive", is_flag=True)
@click.option("-o", "overwrite", help="overwrite old po file", is_flag=True)
@click.option("--split", "shard", help="use shard", is_flag=True)
def run(
    input_token: bool,
    dev: bool,
    token: str,
    level: List[str],
    env_path: Union[str, bool],
    summon_i18n: bool,
    lang: str,
    arg_include_paths: Path,
    recursive: bool,
    overwrite: bool,
    shard: bool,
):
    from .core.logging import init_logging

    init_logging(level=level)

    if summon_i18n:
        if lang == ".":
            lang = ",".join(valid_locales)
        else:
            for _lang in lang.split(","):
                if _lang not in valid_locales:
                    click.echo(f"無效的語言標記 {_lang}")
                    return
        from tool.i18n import main

        main(
            lang=lang,
            arg_include_paths=arg_include_paths,
            recursive=recursive,
            overwrite=overwrite,
        )
        return

    if env_path is not None:
        if isinstance(env_path, str):
            dotenv.load_dotenv(env_path)
        elif env_path:
            dotenv.load_dotenv()

    token = os.getenv("DISCORD_TOKEN")

    if shard:
        # if BOT_SHARD is True use shard connect to discord
        os.environ["BOT_SHARD"] = "1"

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

    from .core.bot import Bot

    Bot(dev=dev, test=True).run(token)


if __name__ == "__main__":
    run()
