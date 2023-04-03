import logging
import traceback
from contextvars import ContextVar
from enum import Enum, auto
from pathlib import Path
from typing import ClassVar, TypeVar, overload

from discord import ApplicationContext as DiscordApplicationContext
from discord import Cog
from discord.commands.core import docs, valid_locales
from discord.ext.commands import Context as DiscordContext

from ..utils import ApplicationContext, Context, I18nCog

log = logging.getLogger(__name__)

_translators: dict[Path, "Translator"] = {}
_file_default_lang = "zh-TW"
_default_lang = ContextVar("_default_lang", default=_file_default_lang)

_CogT = TypeVar("_CogT", bound=Cog | I18nCog)


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
    def __call__(self, untranslated: str, *, local: str | None = None) -> str: ...  # noqa
    @overload
    def __call__(self, untranslated: str, *, local: str | None = None, all: bool = True) -> dict[str, str]: ...  # noqa
    # fmt: on

    def __call__(
        self,
        untranslated: str,
        *,
        local: str | None = None,
        all: bool | None = None,
    ) -> str | dict[str, str]:
        local = local or get_default_locale()
        if all:
            translations = {_file_default_lang: untranslated}
            for lang, translated in self.translations.items():
                translations[lang] = translated.get(untranslated) or untranslated
            return translations

        try:
            return self.translations[local][untranslated]
        except KeyError:
            return untranslated

    def load_translations(self) -> None:
        self.translations = _get_langs_translation(self.locales_path)


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
    for translator in _translators:
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


async def command_before_invoke(
    ctx: DiscordContext | DiscordApplicationContext,
) -> Context | ApplicationContext:
    def _base_translator(*args, **kwargs):
        if kwargs.pop("guild_local"):
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

        return Translator(
            __name__,
            locales_path=Path(traceback.extract_stack()[-2].filename).parent
            / "locales",
        )(*args, local=local, **kwargs)

    setattr(ctx, "_", _base_translator)

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
            Translator(
                __name__,
                locales_path=Path(traceback.extract_stack()[-2].filename).parent
                / "locales",
            )
            if cls is None
            else cls
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
