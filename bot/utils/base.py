from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Type, TypeVar, overload

import discord
from discord import ApplicationContext as DiscordApplicationContext
from discord.ext.commands import Context as DiscordContext


__all__ = (
    "BaseCog",
    "Bot",
    "I18nContext",
    "ApplicationContext",
    "Context",
    "I18nCog",
)

if TYPE_CHECKING:
    from ..core.bot import Bot
    from ..core.i18n import Translator, TranslatorString
else:
    Bot = None

CogT = TypeVar("CogT", bound="BaseCog")


class BaseCogMeta(discord.CogMeta):
    __cog_dev__: bool

    def __new__(cls: Type[CogT], *args: Any, **kwargs: Any) -> CogT:
        name, base, attrs = args

        attrs["__cog_dev__"] = kwargs.pop("dev", False)
        attrs["__translator_name__"] = kwargs.pop("tr_name", {})
        attrs["__translator_description__"] = kwargs.pop("tr_description", {})

        return super().__new__(cls, name, base, attrs, **kwargs)


class BaseCog(discord.Cog, metaclass=BaseCogMeta):
    __cog_dev__: ClassVar[bool]
    __translator_name__: ClassVar[dict[str, str]]
    __translator_description__: ClassVar[dict[str, str]]

    def __init__(self, bot: "Bot") -> None:
        self.bot = bot
        self.log = bot.log
        self.console = bot.console


class I18nContext:
    @overload
    def _(
        self,
        untranslated: str,
        *,
        local: str | None = None,
        guild_local: bool = False,
    ) -> "TranslatorString":
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


class ApplicationContext(I18nContext, DiscordApplicationContext):
    pass


class Context(I18nContext, DiscordContext):
    pass


class I18nCog(Protocol):
    __translator__: ClassVar["Translator"]
