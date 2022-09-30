import inspect
import logging
import os
import platform
from datetime import datetime
from typing import Any, Optional, Union

import discord

from bot import __version__
from bot.core.i18n import I18n

log = logging.getLogger("bot")


class Bot(discord.Bot, object):
    __version__ = __version__

    def __init__(self, *args, dev: bool = False, **kwargs):
        self.dev = dev
        self.log = log
        self._uptime: Optional[datetime] = None
        self.base_lang = os.getenv("BASE_LANG", "zh_TW")

        super().__init__(*args, **kwargs)

        self.before_invoke(I18n.before_invoke)

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
        if isinstance(cog, discord.Cog):
            # https://discord.com/developers/docs/reference#locales
            I18n.set_cog(cog)
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
