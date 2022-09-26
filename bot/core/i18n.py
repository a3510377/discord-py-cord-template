import json
import inspect
from pathlib import Path
from typing import Dict, TypedDict, Union

import yaml
import discord
from discord import SlashCommand, SlashCommandGroup


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


class I18n:
    def load_i18n_file(
        self,
        i18n_dir: Union[str, Path],
        file_name: str,
    ) -> I18nFileDataType:
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

    def set_cog(self, cog: discord.Cog) -> None:
        if isinstance(cog, discord.Cog):
            cog_file = Path(inspect.getfile(cog.__class__))
            i18n_dir: Path = cog_file.parent / "i18n"

            # https://discord.com/developers/docs/reference#locales
            local = self.load_i18n_file(i18n_dir, cog_file.stem)

            for command in cog.__cog_commands__:
                self.set_slash_command(command, local)

    def set_slash_command(
        self,
        command: Union[SlashCommand, SlashCommandGroup],
        local_map: I18nFileDataType,
    ) -> None:
        if isinstance(command, (SlashCommand, SlashCommandGroup)):
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

                for arg_name, data in lang_data.get("args", {}).items():
                    local_args[arg_name] = local_args.get(arg_name, {})
                    local_args[arg_name][lang] = local_args.get(
                        local_args[arg_name].get(lang), {}
                    )

                    if not data:
                        continue

                    if name := lang_data.get("name"):
                        local_args[arg_name][lang]["name"] = name
                    if description := lang_data.get("description"):
                        local_args[arg_name][lang]["description"] = description

            if command.name_localizations is None:
                command.name_localizations = {}
            if command.description_localizations is None:
                command.description_localizations = {}

            command.name_localizations.update(local_name)
            command.description_localizations.update(local_description)

            # TODO add args i18n
            # for arg in command.options:
            #     local_arg = local_args.get(arg._parameter_name)

            #     print("local_arg: ", local_arg)
            #     # local_arg.get("name")
            #     arg.name_localizations
            #     arg.description_localizations
            #     # local_arg.get("description")
