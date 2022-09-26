import inspect
import json
import logging
import platform
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, Union
import discord
from bot import __version__

log = logging.getLogger("bot")


class Bot(discord.Bot):
    __version__ = __version__

    def __init__(self, *args, dev: bool = False, **kwargs):
        self.dev = dev
        self.log = log
        self._uptime: Optional[datetime] = None

        super().__init__(*args, **kwargs)

        self.load_extension("bot.core.events")
        self.load_extension("bot.cogs", recursive=True)

    async def get_or_fetch_user(self, user_id: Union[int, str]) -> discord.User:
        if (user := self.get_user(user_id := int(user_id))) is not None:
            return user
        return await self.fetch_user(user_id)

    async def get_or_fetch_member(
        self, guild: discord.Guild, member_id: Union[int, str]
    ):
        if (member := guild.get_member(member_id := int(member_id))) is not None:
            return member
        return await guild.fetch_member(guild, member_id)

    async def get_or_fetch_channel(self, channel_id: Union[int, str]):
        if (channel := self.get_channel(channel_id := int(channel_id))) is not None:
            return channel
        return await self.fetch_channel(channel_id)

    def add_cog(self, cog: discord.Cog, *, override: bool = False) -> None:
        SlashCommand = (discord.SlashCommand, discord.SlashCommandGroup)

        if isinstance(cog, discord.Cog):
            cog_file = Path(inspect.getfile(cog.__class__))
            i18n_dir: Path = cog_file.parent / "i18n"

            # https://discord.com/developers/docs/reference#locales
            local: Dict[str, str] = {}
            if (i18n_file := i18n_dir / f"{cog_file.stem}.json").is_file():
                local = json.loads(i18n_file.read_text(encoding="utf-8"))

            for command in cog.__cog_commands__:
                if isinstance(command, SlashCommand):
                    command: Union[discord.SlashCommand, discord.SlashCommandGroup]

                    command.description_localizations = local.get(command.name)
        super().add_cog(cog, override=override)

    def fix_doc(self, *doc: str):
        return inspect.cleandoc("\n".join(doc))

    def run(self, *args: Any, **kwargs: Any):
        for msg in self.fix_doc(
            f"""
            [red]python version: [/red][cyan]{platform.python_version()}[/cyan]
            [red]py-cord version: [/red][cyan]{discord.__version__}[/cyan]
            [red]bot version: [/red][cyan]{self.__version__}[/cyan]
            """
        ).split("\n"):
            log.info(msg)

        super().run(*args, **kwargs)
