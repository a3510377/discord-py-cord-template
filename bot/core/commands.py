import inspect
from typing import Dict

import discord
from discord import (
    AutocompleteContext,
    ButtonStyle,
    ExtensionAlreadyLoaded,
    Interaction,
)
from discord import ui as Ui
from discord.ext import commands
from discord.utils import basic_autocomplete

from bot import (
    ApplicationContext,
    BaseCog,
    Bot,
    Translator,
    get_absolute_name_from_path,
    reload_locales,
)

_ = Translator(__name__)


class CogConnectionView(Ui.View):
    def __init__(self, bot: "Bot"):
        super().__init__(timeout=None)

        self.bot = bot

    def get_cogs(self):
        return [
            get_absolute_name_from_path(inspect.getfile(cog.__class__))
            for cog in self.bot.cogs.values()
        ]

    @Ui.button(
        label="重載所有已加載的擴展",
        style=ButtonStyle.green,
        custom_id="persistent_view:cog_connection:reload_all",
    )
    async def reload_all(self, _: Ui.Button, interaction: Interaction):
        done_count = 0
        errors: Dict[str, Exception] = {}

        for name in self.get_cogs():
            try:
                self.bot.reload_extension(name)
                done_count += 1
            except Exception as error:
                self.bot.log.exception(type(error).__name__, exc_info=error)
                errors.__setitem__(name, error)

        embed = discord.Embed(
            title="重新加載擴展",
            description=f"成功重新加載 {done_count} 個擴展\n{len(errors)} 個錯誤",
        )

        for name, er in errors.items():
            embed.add_field(name=name, value=str(er))

        await interaction.message.edit(
            content="",
            embed=embed,
            view=None,
        )

    @Ui.button(
        label="加載 cogs 中的新擴展",
        style=ButtonStyle.red,
        custom_id="persistent_view:cog_connection:load_cogs",
    )
    async def load_cogs(self, _: Ui.Button, interaction: Interaction):
        old_cog_count = len(self.bot.cogs)
        errors = self.bot.load_extension("bot.cogs", recursive=True, store=True)
        embed = discord.Embed(
            title="加載完成",
            description=f"共加載 {old_cog_count - len(self.bot.cogs)} 個擴展",
        )

        for name, error in errors.items():
            if isinstance(error, ExtensionAlreadyLoaded):
                continue

            self.bot.log.exception(type(error).__name__, exc_info=error)
            embed.add_field(name=name, value=error)

        await interaction.message.edit(content=None, embed=embed, view=None)


async def get_command(ctx: AutocompleteContext):
    bot: Bot = ctx.bot

    return [cmd.name for cmd in bot.all_commands.values()]


class BaseCommandsCog(BaseCog, name="核心"):
    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(CogConnectionView(self.bot))

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: ApplicationContext):
        reload_locales()
        await ctx.send(
            "請選取您要的模式",
            view=CogConnectionView(self.bot),
        )

    @discord.slash_command(guild_only=True)
    @discord.option(
        "command",
        str,
        i18n_name=_("指令"),
        i18n_description=_("要查詢的指令"),
        autocomplete=basic_autocomplete(get_command),
        default=None,
    )
    async def help(self, ctx: ApplicationContext, command: str):
        view = await self.bot.help(ctx)

        await ctx.respond(
            embed=view.get_page()
            if command is None
            else view.get_page(command, page=False),
            view=view,
            ephemeral=True,
        )


def setup(bot: "Bot"):
    bot.add_cog(BaseCommandsCog(bot))
