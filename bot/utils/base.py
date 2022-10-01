from typing import (
    Any,
    ClassVar,
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)

import discord
from discord import (
    ApplicationContext as DiscordApplicationContext,
)
from discord.ext.commands import Context as DiscordContext


__all__ = (
    "BaseCog",
    "Bot",
    "I18nContext",
    "ApplicationContext",
    "Context",
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
    # typeof: import bot.core.i18n from command_before_invoke
    @overload
    def _(self) -> Dict[str, Union[str, List[Any]]]:
        ...

    # typeof: import bot.core.i18n from command_before_invoke
    @overload
    def _(
        self,
        key: str,
        default: Optional[str] = None,
        *,
        default_lang: Optional[str] = None,
        **kwargs: str,
    ) -> Optional[str]:
        ...

    # typeof: import bot.core.i18n from command_before_invoke
    def _():
        raise NotImplementedError


class ApplicationContext(I18nContext, DiscordApplicationContext):
    pass


class Context(I18nContext, DiscordContext):
    pass
