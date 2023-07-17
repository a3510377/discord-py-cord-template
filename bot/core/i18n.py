from __future__ import annotations

import logging
import traceback
from collections import UserDict
from contextvars import ContextVar
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, TypeVar, overload

from discord import ApplicationContext as DiscordApplicationContext
from discord import Cog, ContextMenuCommand, Member, SlashCommand, User
from discord.commands.core import docs, valid_locales
from discord.ext.commands import Context as DiscordContext

if TYPE_CHECKING:
    from ..utils import ApplicationContext, Context, I18nCog

log = logging.getLogger(__name__)

_translators: dict[Path, "Translator"] = {}
_file_default_lang = "zh-TW"
_default_lang = ContextVar("_default_lang", default=_file_default_lang)

_CogT = TypeVar("_CogT", bound="Cog | I18nCog")
_CommandT = TypeVar("_CommandT", bound=SlashCommand | ContextMenuCommand)


class _po_parse_step(Enum):
    NULL = auto
    MSGID = auto
    MSGSTR = auto


class Translator:
    locales_path: ClassVar[Path]

    def __new__(cls, *_, **kwargs):
        locales_path = kwargs.pop("locales_path", None)

        if locales_path in _translators:
            return _translators.get(locales_path)

        self = super().__new__(cls)
        self.locales_path = Path(
            locales_path
            if locales_path
            else Path(traceback.extract_stack()[-2].filename).parent / "locales"
        )
        _translators[self.locales_path] = self
        return self

    # locales_path is type hint, accomplish in __new__
    def __init__(self, name: str, locales_path: str | None = None) -> None:
        self.name = name

        self.translations: dict[str, dict[str, str]] = {}  # dict[lang, dict[key, str]]
        self.load_translations()

    # fmt: off
    @overload
    def __call__(self, untranslated: str, *, local: str | None = None) -> "TranslatorString": ...  # noqa
    @overload
    def __call__(self, untranslated: str, *, local: str | None = None, all: bool = True) -> dict[str, str]: ...  # noqa
    # fmt: on

    def __call__(
        self,
        untranslated: str,
        *,
        local: str | None = None,
        all: bool | None = None,
        **kwargs,
    ) -> "TranslatorString" | dict[str, str]:
        local = local or get_default_locale()

        translations = {_file_default_lang: untranslated}
        for lang, translated in self.translations.items():
            translations[lang] = translated.get(untranslated) or untranslated

        if all:
            return translations

        try:
            untranslated = self.translations[local][untranslated]
        except KeyError:
            pass

        return TranslatorString(untranslated, translations)

    def load_translations(self) -> None:
        self.translations = _get_langs_translation(self.locales_path)


class TranslatorString(UserDict):
    def __init__(self, str_data: str, dict_data: dict[str, str]) -> None:
        self.str_data = str_data
        self.data = dict_data

    def __repr__(self) -> str:
        return self.str_data

    def __str__(self) -> str:
        return self.str_data

    @classmethod
    def from_str(cls, str_data: str | TranslatorString) -> TranslatorString:
        if isinstance(str_data, TranslatorString):
            return str_data
        return cls(str_data, {k: str_data for k in valid_locales})

    # fmt: off
    @overload
    def format(self, *args: str, **kwargs: str) -> str: ...  # noqa
    @overload
    def format(self, *args: object, **kwargs: object) -> str: ...  # noqa
    # fmt: on

    def format(self, *args, **kwargs):
        return str(self).format(*args, **kwargs)


def get_default_locale() -> str:
    return _default_lang.get()


def set_default_locale(locale: str) -> None:
    if locale not in valid_locales:
        raise ValueError(
            f"Locale {locale!r} is not a valid locale, see {docs}/reference#locales for"
            " list of supported locales."
        )

    _default_lang.set(locale)


def reload_locales() -> None:
    log.info("Reloading locales")
    for translator in _translators.values():
        translator.load_translations()


def _get_langs_translation(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_dir():
        return {}

    translations = dict.fromkeys(valid_locales, dict[str, str]())

    for path in path.iterdir():
        file_lang = path.stem
        if path.is_file() and path.suffix == ".po" and file_lang in valid_locales:
            translations[file_lang] = _parse(path.read_text(encoding="utf-8"))
        elif file_lang != "base":
            log.warn(f"Unexpected filename, 'invalid' file: {path}")
    return translations


def _parse(file_content: str) -> dict[str, str]:
    translations = {}
    step, untranslated, translated = _po_parse_step.NULL, "", ""

    for line in file_content.splitlines():
        line = line.strip()

        if line.startswith('msgid "'):
            if step == _po_parse_step.MSGSTR and translated:
                translations[_unescape(untranslated)] = _unescape(translated)
            step = _po_parse_step.MSGID
            untranslated = line[7:-1]
        elif line.startswith('"') and line.endswith('"'):
            if step == _po_parse_step.MSGID:
                untranslated += line[1:-1]
            elif step == _po_parse_step.MSGSTR:
                translated += line[1:-1]
        elif line.startswith('msgstr "'):
            step = _po_parse_step.MSGSTR
            translated = line[8:-1]

        if step is _po_parse_step.MSGSTR and translated:
            translations[_unescape(untranslated)] = _unescape(translated)

    return translations


def _unescape(string):
    return (
        string.replace(r"\\", "\\")
        .replace(r"\t", "\t")
        .replace(r"\r", "\r")
        .replace(r"\n", "\n")
        .replace(r"\"", '"')
    )


def from_ctx_get_local(
    ctx: DiscordContext | DiscordApplicationContext,
    guild_local: str | None = None,
    **kwargs,
) -> str:
    if guild_local:
        if isinstance(ctx, DiscordApplicationContext):
            local = ctx.guild_locale
        else:
            local = ctx.guild.preferred_locale
    else:
        local = (
            ctx.locale
            if isinstance(ctx, DiscordApplicationContext)
            else ctx.guild.preferred_locale
        )

    return local or get_default_locale()


def from_user_get_local(user: User | Member, **kwargs) -> str:
    return user.guild.preferred_locale or get_default_locale()


async def command_before_invoke(
    ctx: DiscordContext | DiscordApplicationContext,
) -> "Context" | "ApplicationContext":
    def _base_translator(*args, **kwargs):
        return Translator(
            __name__,
            locales_path=Path(traceback.extract_stack()[-2].filename).parent
            / "locales",
        )(*args, local=from_ctx_get_local(ctx, **kwargs), **kwargs)

    ctx.__dict__["local"] = lambda **kwargs: from_ctx_get_local(ctx, **kwargs)
    ctx.__dict__["_"] = _base_translator

    return ctx


def cog_i18n(cls: type | Translator | None = None):
    """
    @cog_i18n(_)
    @cog_i18n()
    @cog_i18n
    """

    def decorator(cog_class: type[_CogT]) -> type[_CogT]:
        if hasattr(cog_class, "__translator__"):
            return cog_class

        tr = (
            cls
            if isinstance(cls, Translator)
            else Translator(
                __name__,
                locales_path=Path(traceback.extract_stack()[-2].filename).parent
                / "locales",
            )
        )

        setattr(cog_class, "__translator__", tr)
        setattr(cog_class, "__translator_name__", tr(cog_class.__cog_name__, all=True))
        setattr(
            cog_class,
            "__translator_description__",
            tr(cog_class.__cog_description__, all=True),
        )

        return cog_class

    if not isinstance(cls, Translator) and cls is not None:
        return decorator(cls)
    return decorator


def i18n_command(command: _CommandT) -> _CommandT:
    kwargs = command.__original_kwargs__

    if command.name_localizations is None:
        command.name_localizations = {}

    if isinstance(name := kwargs.get("i18n_name", None), TranslatorString):
        command.name_localizations |= dict(name)

    if isinstance(command, SlashCommand):
        if command.description_localizations is None:
            command.description_localizations = {}

        if isinstance(description := kwargs.get("i18n_description"), TranslatorString):
            command.description_localizations |= dict(description)

        for option in command.options:
            if isinstance(option.name, TranslatorString):
                if option.name_localizations is None:
                    command.name_localizations = {}
                command.name_localizations |= dict(option.name)

            if isinstance(option.description, TranslatorString):
                if option.description_localizations is None:
                    command.description_localizations = {}
                command.description_localizations |= dict(option.description)

    return command
