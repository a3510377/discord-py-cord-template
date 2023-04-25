from discord import ApplicationCommand, Interaction, SelectOption
from discord.ext.commands import Command
from discord.ui import Select, View, select
from discord.utils import async_all

from bot import ApplicationContext, Bot, Context


class HelpView(View):
    def __init__(self, bot: "Bot") -> None:
        super().__init__()

        self.bot = bot

    async def setup(self, ctx: ApplicationContext | Context) -> None:
        bot = self.bot

        commands: list[ApplicationCommand] = []
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

            commands.append(cmd)

        for cmd in bot.prefixed_commands.values():
            if not await async_all(predicate(ctx) for predicate in cmd.checks):
                continue

            prefixed_commands.append(cmd)

        select: Select = self.get_item("__core_help_view_select_help")
        options = select.options

        options.append(
            SelectOption(
                label="1",
                value="test",
                description="3",
            )
        )

    @select(custom_id="__core_help_view_select_help")
    async def select_help(self, select: Select, interaction: Interaction):
        print(select.values[0])
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="timeout", view=self)
