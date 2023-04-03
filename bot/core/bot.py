import logging
import os
from datetime import datetime
from typing import Any, Optional, Union

import discord
import rich
from discord import ApplicationCommand, Intents
from discord.ext import commands

from bot import __version__, command_before_invoke, set_default_locale

log = logging.getLogger("bot")


class Bot(commands.Bot):
    __version__ = __version__

    def __init__(self, *args, dev: bool = False, **kwargs):
        self.dev = dev
        self.log = log
        self._uptime: Optional[datetime] = None
        self.base_lang = kwargs.pop("lang", os.getenv("BASE_LANG", "zh-TW"))
        self.console = rich.get_console()

        set_default_locale(self.base_lang)

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

        self.before_invoke(command_before_invoke)
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
        self,
        guild: discord.Guild,
        member_id: Union[int, str],
    ):
        if (member := guild.get_member(member_id := int(member_id))) is not None:
            return member
        return await guild.fetch_member(member_id)

    async def get_or_fetch_channel(self, channel_id: Union[int, str]):
        if (channel := self.get_channel(channel_id := int(channel_id))) is not None:
            return channel
        return await self.fetch_channel(channel_id)

    def add_cog(self, cog: discord.Cog, *, override: bool = False) -> None:
        # https://discord.com/developers/docs/reference#locales
        super().add_cog(cog, override=override)

        self.log.info(f"cog {cog.__cog_name__} 加載完成")

    def add_application_command(self, command: ApplicationCommand) -> None:
        command.name
        super().add_application_command(command)

    def remove_cog(self, name: str) -> None:
        if cog := super().remove_cog(name):
            self.log.info(f"cog {cog.__cog_name__} 移除完成")

    def run(self, *args: Any, **kwargs: Any):
        super().run(*args, **kwargs)
