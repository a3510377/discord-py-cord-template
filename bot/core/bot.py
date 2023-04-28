import logging
import os
from datetime import datetime
from typing import Any, Optional, Union

import discord
import rich
from discord import ApplicationCommand, AutoShardedClient, Embed, Intents
from discord.ext import commands

from bot import (
    ApplicationContext,
    Context,
    __version__,
    command_before_invoke,
    i18n_command,
    set_default_locale,
)

from .help import HelpView

log = logging.getLogger("bot")


class _BotMeta(type):
    def __new__(cls, *args: Any, **kwargs: Any):
        name, base, attrs = args

        if os.getenv("BOT_SHARD"):
            log.info("使用分片啟動")
            return type(name, (AutoShardedClient, *base), attrs, **kwargs)

        return super().__new__(cls, name, base, attrs, **kwargs)


class BotMeta(_BotMeta, type(commands.Bot)):
    pass


class Bot(commands.Bot, metaclass=BotMeta):
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
        i18n_command(command)

        super().add_application_command(command)

    def remove_cog(self, name: str) -> None:
        if cog := super().remove_cog(name):
            self.log.info(f"cog {cog.__cog_name__} 移除完成")

    async def help(self, ctx: ApplicationContext | Context) -> HelpView:
        modal = HelpView(self)

        await modal.setup(ctx)

        return modal

    def set_authorization_embed(self, embed: Embed) -> Embed:
        user = self.user

        embed.set_author(
            name=user.name,
            icon_url=user.display_avatar,
            url="https://github.com/a3510377/discord-py-cord-template",
        )
        embed.set_footer(
            text="© 開發模板由 a3510377 製作",
            icon_url="https://avatars.githubusercontent.com/u/70706886",
        )
        embed.timestamp = datetime.now()

        return embed
