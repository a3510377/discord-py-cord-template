from collections import defaultdict

from discord import Cog, Embed, Interaction, SelectOption
from discord.ext.commands import Command
from discord.ui import Select, View, select
from discord.utils import async_all

from bot import ApplicationContext, BaseCog, Bot, Context


class HelpView(View):
    def __init__(self, bot: "Bot") -> None:
        super().__init__(timeout=60)

        self.bot = bot
        self.pages = defaultdict[str, Embed](Embed)
        self.pages_select_options = dict[str, SelectOption]()

    async def setup(self, ctx: ApplicationContext | Context) -> None:
        bot = self.bot

        prefixed_commands: list[Command] = []
        for cmd in bot.application_commands:
            if cmd.guild_only and ctx.guild is None:
                # for dm
                continue

            if isinstance(ctx, ApplicationContext):
                if (
                    cmd.default_member_permissions is not None
                    and cmd.default_member_permissions <= ctx.app_permissions
                ):
                    # check command permissions
                    continue
            else:
                if (
                    cmd.default_member_permissions is not None
                    and cmd.default_member_permissions <= ctx.author.guild_permissions
                ):
                    continue

            cog = cmd.cog
            if cog:
                cog: Cog
                if isinstance(cog, BaseCog):
                    lang = ctx.local()
                    option = SelectOption(
                        label=cog.__translator_name__.get(lang),
                        description=cog.__translator_description__.get(lang),
                    )
                else:
                    option = SelectOption(
                        label=cog.qualified_name,
                        description=cog.description,
                    )

                option.value = (class_name := cog.__class__.__name__)
                self.pages_select_options[class_name] = option

        for cmd in bot.prefixed_commands.values():
            if not await async_all(predicate(ctx) for predicate in cmd.checks):
                continue

            prefixed_commands.append(cmd)

        select: Select = self.get_item("__core_help_view_select_help")
        select.options.clear()
        select.options.extend(self.pages_select_options.values())

    @select(custom_id="__core_help_view_select_help")
    async def select_help(self, select: Select, interaction: Interaction):
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="timeout", view=self)
