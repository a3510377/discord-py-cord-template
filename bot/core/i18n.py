import json
import inspect
from pathlib import Path
from typing import Dict, List, Optional, TypedDict, Union

import yaml
import discord
from discord import SlashCommand, SlashCommandGroup

from bot.utils import set_dict_default


class CommandI18nDataType(TypedDict):
    name: str
    description: str


class BaseI18nDataType(TypedDict):
    name: str
    description: str
    args: "CommandArgsDataType"


CommandArgsDataType = Dict[str, CommandI18nDataType]
CommandArgsI18nDataType = Dict[str, CommandArgsDataType]
I18nFileDataType = Dict[str, Dict[str, BaseI18nDataType]]
LocalCommandsType = Union[SlashCommand, SlashCommandGroup]


class I18n:
    # @overload
    # def __init__(self, *, cog: discord.Cog) -> None:
    #     """get i18n from cog"""
    #     ...

    # @overload
    # def __init__(self, *, path: Union[str, Path], file_name: str) -> None:
    #     """get i18n from file"""
    #     ...

    # @overload
    # def __init__(self, *, command: LocalCommandsType) -> None:
    #     """get i18n from command"""
    #     ...

    # def __init__(
    #     self,
    #     *,
    #     cog: Optional[discord.Cog] = None,
    #     path: Optional[Union[str, Path]] = None,
    #     file_name: Optional[str] = None,
    #     command: Optional[LocalCommandsType] = None,
    # ) -> None:
    #     self.local = None

    #     if cog is not None:
    #         self.cog = cog
    #         self.local = I18n.get_cog_i18n_file(cog)
    #     elif path is not None:
    #         if file_name is None:
    #             raise ValueError("MISS filename")

    #         self.local = I18n.load_i18n_file(cog, file_name)
    #     elif command is not None:
    #         self.command = command
    #         self.local = I18n.get_cog_i18n_file(cog)

    @staticmethod
    def load_i18n_file(
        i18n_dir: Union[str, Path],
        file_name: str,
    ) -> Optional[I18nFileDataType]:
        if (
            (i18n_file := Path(i18n_dir) / f"{file_name}.json").is_file()
            or (i18n_file := Path(i18n_dir) / f"{file_name}.yml").is_file()
            or (i18n_file := Path(i18n_dir) / f"{file_name}.yaml").is_file()
        ):
            file_extension = i18n_file.suffix[1:]
            data = i18n_file.read_text(encoding="utf-8")

            if file_extension == "json":
                return json.loads(data)
            else:
                return yaml.safe_load(data)

        return None

    @staticmethod
    def get_cog_i18n_file(cog: discord.Cog) -> Optional[I18nFileDataType]:
        if isinstance(cog, discord.Cog):
            cog_file = Path(inspect.getfile(cog.__class__))
            i18n_dir: Path = cog_file.parent / "i18n"

            # https://discord.com/developers/docs/reference#locales
            return I18n.load_i18n_file(i18n_dir, cog_file.stem)

    @staticmethod
    def set_cog(cog: discord.Cog) -> None:
        local = I18n.get_cog_i18n_file(cog)

        for command in cog.__cog_commands__:
            I18n.set_slash_command(command, local)

    @staticmethod
    def set_slash_command(
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
