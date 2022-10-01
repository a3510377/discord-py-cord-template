import json
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union, TYPE_CHECKING, overload

import yaml
import discord
from discord import (
    ApplicationContext,
    SlashCommand,
    SlashCommandGroup,
)
from discord.ext.commands import Context

from bot.utils import set_dict_default

if TYPE_CHECKING:
    from bot import Bot


class CommandI18nDataType(TypedDict):
    name: str
    description: str


class BaseI18nDataType(TypedDict):
    name: str
    description: str
    args: "CommandArgsDataType"
    messages: "MessagesType"


# Dict[arg_name, CommandI18nDataType]
CommandArgsDataType = Dict[str, CommandI18nDataType]
# Dict[lang_name, BaseI18nDataType]
LocalsI18nDataType = Dict[str, BaseI18nDataType]
# Dict[command_name, LocalsI18nDataType]
I18nFileDataType = Dict[str, LocalsI18nDataType]
LocalCommandsType = Union[SlashCommand, SlashCommandGroup]

MessageListType = List[Any]
MessageDictType = Dict[str, str]
MessagesType = Dict[str, Union[MessageListType, MessageDictType, "MessagesType"]]
# Dict[lang_name, CommandArgsDataType]
CommandArgsI18nDataType = Dict[str, CommandArgsDataType]


@overload
def get(
    locals: LocalsI18nDataType,
    key: str,
    default: Optional[str] = None,
    *,
    lang: str,
    **kwargs: Any,
) -> Optional[str]:
    ...


@overload
def get(locals: LocalsI18nDataType) -> Dict[str, Union[str, List[Any]]]:
    ...


def get(
    locals: LocalsI18nDataType,
    key: Optional[str] = None,
    default: Optional[str] = None,
    *,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> Union[Optional[str], Dict[str, Union[str, List[Any]]]]:
    if lang and (local := locals.get(lang)):
        keys = key.split(".")
        value = local.get("messages")

        for k in keys:
            if isinstance(value, dict) and (value := value.get(k)):
                pass
            else:
                value = key if default is None else default

        return value.format_map(kwargs)

    output: Dict[str, Union[str, List[Any]]] = {}

    def get_key(key: List[str], value: MessagesType):
        if isinstance(value, (list, str)):
            output[key.join(".")] = value
        else:
            for k, data in value.items():
                get_key([*key, k], data)

    get_key([], locals)
    return output


async def command_before_invoke(ctx: Union[Context, ApplicationContext]):
    bot: "Bot" = ctx.bot

    command = ctx.command
    command_file = Path(inspect.getfile(command.callback))
    locals = load_i18n_file_from_file(command_file).get(command.name, {})

    locale = (
        ctx.locale
        if isinstance(ctx, ApplicationContext)
        else ctx.guild.preferred_locale
    ) or bot.base_lang

    ctx.__dict__.update(
        {"_": lambda *args, **kwargs: get(locals, *args, lang=locale, **kwargs)}
    )


def load_i18n_file_from_file(path: Union[str, Path]) -> Optional[I18nFileDataType]:
    if not (path := Path(path)).is_file():
        raise ValueError("path must be a file")

    i18n_dir = path.parent / "i18n"
    file_name = path.stem

    # https://discord.com/developers/docs/reference#locales
    if (
        (i18n_file := Path(i18n_dir) / f"{file_name}.json").is_file()
        or (i18n_file := Path(i18n_dir) / f"{file_name}.yml").is_file()
        or (i18n_file := Path(i18n_dir) / f"{file_name}.yaml").is_file()
    ):
        file_extension = i18n_file.suffix[1:]
        data = i18n_file.read_text(encoding="utf-8")

        if file_extension == "json":
            return json.loads(data)

        return yaml.safe_load(data)


def load_i18n_file(
    i18n_dir: Union[str, Path],
    file_name: str,
) -> Optional[I18nFileDataType]:
    return load_i18n_file_from_file(Path(i18n_dir) / file_name)


def get_cog_i18n_file(cog: discord.Cog) -> Optional[I18nFileDataType]:
    if isinstance(cog, discord.Cog):
        return load_i18n_file_from_file(inspect.getfile(cog.__class__))


def set_cog(cog: discord.Cog) -> None:
    local = get_cog_i18n_file(cog)

    for command in cog.__cog_commands__:
        set_slash_command_local(command, local)


def set_slash_command_local(
    command: LocalCommandsType,
    local_map: Optional[I18nFileDataType],
) -> None:
    if isinstance(command, (SlashCommand, SlashCommandGroup)) and local_map:
        local_command = local_map.get(command.name)

        if local_command is None:
            return

        local_name: Dict[str, str] = {}
        local_description: Dict[str, str] = {}
        local_args: CommandArgsI18nDataType = {}

        for lang in local_command.keys():
            lang_data = local_command[lang]

            if name := lang_data.get("name"):
                local_name[lang] = name
            if description := lang_data.get("description"):
                local_description[lang] = description

            for arg_name, data in (lang_data.get("args") or {}).items():
                set_dict_default(local_args, arg_name, {})
                set_dict_default(local_args[arg_name], "name", {})
                set_dict_default(local_args[arg_name], "description", {})

                if not data:
                    continue

                if name := data.get("name"):
                    local_args[arg_name]["name"][lang] = name
                if description := data.get("description"):
                    local_args[arg_name]["description"][lang] = description

        set_dict_default(command, "name_localizations", {})
        set_dict_default(command, "description_localizations", {})

        command.name_localizations.update(local_name)
        command.description_localizations.update(local_description)

        args: List[discord.Option] = command._parse_options(
            command._get_signature_parameters(),
            check_params=True,
            # pass ctx
        )[1:]
        for arg in args:
            set_dict_default(arg, "name_localizations", {})
            set_dict_default(arg, "description_localizations", {})

            local_arg = local_args.get(arg._parameter_name, {})
            arg.name_localizations.update(local_arg.get("name", {}))
            arg.description_localizations.update(local_arg.get("description", {}))
