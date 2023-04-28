from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Type, TypeVar, overload

import discord
from discord import ApplicationContext as DiscordApplicationContext
from discord.ext.commands import Context as DiscordContext

from bot.utils.util import fix_doc

__all__ = (
    "BaseCog",
    "Bot",
    "I18nContext",
    "ApplicationContext",
    "Context",
    "I18nCog",
)

from ..core.i18n import Translator, TranslatorString

if TYPE_CHECKING:
    from ..core.bot import Bot
else:
    Bot = None

_CogT = TypeVar("_CogT", bound="BaseCog")


class BaseCogMeta(discord.CogMeta):
    """
    A metaclass for defining a cog.

    Attributes:
    -----------
    dev: bool
        A easily extensible option will add a static variable `__cog_dev__`
        to the target class for ease of development.
    name: str
        Add a static variable `__translator_name__` to get name
        to store the multilingual name.
    description: str
        Add a static variable `__translator_description__` to get description
        to store the multilingual description. If you don't include the setting,
        you automatically get the `__doc__` in the taxonomy.
    """

    __cog_dev__: bool

    def __new__(
        cls: Type[_CogT],
        *args: Any,
        tr_name: TranslatorString | None = None,
        tr_description: TranslatorString | None = None,
        **kwargs: Any,
    ) -> _CogT:
        name, base, attrs = args

        attrs["__cog_dev__"] = kwargs.pop("dev", False)
        attrs["__translator_name__"] = tr_name or TranslatorString.from_str(
            kwargs.get("name", name)
        )
        attrs[
            "__translator_description__"
        ] = tr_description or TranslatorString.from_str(
            kwargs.get("description", fix_doc(attrs.get("__doc__", "")))
        )

        return super().__new__(cls, name, base, attrs, **kwargs)


class BaseCog(discord.Cog, metaclass=BaseCogMeta):
    __cog_dev__: ClassVar[bool]
    __translator_name__: ClassVar[TranslatorString]
    __translator_description__: ClassVar[TranslatorString]

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
    def local(guild_local: bool = None) -> str:
        raise NotImplementedError

    # typeof: import bot.core.i18n from command_before_invoke
    def _() -> ...:
        raise NotImplementedError


class ApplicationContext(I18nContext, DiscordApplicationContext):
    pass


class Context(I18nContext, DiscordContext):
    pass


class I18nCog(Protocol):
    __translator__: ClassVar["Translator"]
