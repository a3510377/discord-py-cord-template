from typing import TYPE_CHECKING, Any, ClassVar, Type, TypeVar, overload

import discord

from discord import ApplicationContext as DiscordApplicationContext
from discord.ext.commands import Context as DiscordContext

__all__ = (
    "BaseCog",
    "Bot",
)

if TYPE_CHECKING:
    from ..core.bot import Bot
else:
    Bot = None

CogT = TypeVar("CogT", bound="BaseCog")


class BaseCogMeta(discord.CogMeta):
    __cog_dev__: bool

    def __new__(cls: Type[CogT], *args: Any, **kwargs: Any) -> CogT:
        name, base, attrs = args

        attrs["__cog_dev__"] = kwargs.pop("dev", False)

        return super().__new__(cls, name, base, attrs, **kwargs)


class BaseCog(discord.Cog, metaclass=BaseCogMeta):
    __cog_dev__: ClassVar[bool]

    def __init__(self, bot: "Bot") -> None:
        self.bot = bot
        self.log = bot.log


class I18nContext:
    @overload
    def _(
        self,
        untranslated: str,
        *,
        local: str | None = None,
        guild_local: bool = False,
    ) -> str:
        ...

    @overload
    def _(
        self,
        untranslated: str,
        *,
        local: str | None = None,
        guild_local: bool = False,
        all: bool = True,
    ) -> dict[str, str]:
        ...

    # typeof: import bot.core.i18n from command_before_invoke
    def _() -> ...:
        raise NotImplementedError


# typeof: import bot.core.i18n from command_before_invoke
class ApplicationContext(I18nContext, DiscordApplicationContext):
    pass


# typeof: import bot.core.i18n from command_before_invoke
class Context(I18nContext, DiscordContext):
    pass
