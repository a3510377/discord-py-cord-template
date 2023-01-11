import logging
import os
import platform
from datetime import datetime
from typing import Any, Optional, Union

import discord
from discord import Intents
from discord.ext import commands

from bot import __version__
from bot.utils import fix_doc
from bot.core.i18n import (
    command_before_invoke as i18n_before_invoke,
    set_cog as i18n_set_cog,
)

log = logging.getLogger("bot")


class Bot(commands.Bot):
    __version__ = __version__

    def __init__(self, *args, dev: bool = False, **kwargs):
        self.dev = dev
        self.log = log
        self._uptime: Optional[datetime] = None
        self.base_lang = os.getenv("BASE_LANG", "zh_TW")

        intents = Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            help_command=None,
            intents=intents,
            *args,
            **kwargs,
        )

        self.owner_ids = {int(id) for id in os.getenv("OWNER_IDS", "").split(",")}
        self.before_invoke(i18n_before_invoke)

        self.load_extension("bot.core.events")
        self.load_extension("bot.core.commands")
        self.load_extension("bot.cogs", recursive=True)

    @property
    def uptime(self) -> Optional[datetime]:
        return self._uptime

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
            i18n_set_cog(cog)
        super().add_cog(cog, override=override)

        self.log.info(f"cog {cog.__cog_name__} 加載完成")

    def remove_cog(self, name: str) -> None:
        if cog := super().remove_cog(name):
            self.log.info(f"cog {cog.__cog_name__} 移除完成")

    def run(self, *args: Any, **kwargs: Any):
        for msg in fix_doc(
            f"""
            [red]python version: [/red][cyan]{platform.python_version()}[/cyan]
            [red]py-cord version: [/red][cyan]{discord.__version__}[/cyan]
            [red]bot version: [/red][cyan]{self.__version__}[/cyan]
            """
        ).split("\n"):
            log.info(msg)

        super().run(*args, **kwargs)
