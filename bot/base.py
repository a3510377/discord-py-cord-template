from typing import TYPE_CHECKING, Any, ClassVar, Type, TypeVar

import discord

__all__ = ("BaseCog", "Bot")


if TYPE_CHECKING:
    from .core.bot import Bot
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
