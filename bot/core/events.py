import platform
from datetime import datetime

import discord
from discord import DiscordException
from discord.ext.commands import CommandError, CommandNotFound, Context, NotOwner
from rich.box import MINIMAL
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from bot import ApplicationContext, BaseCog, Bot, Translator

_ = Translator(__name__)


class BaseEventsCog(BaseCog):
    @discord.Cog.listener()
    async def on_ready(self):
        bot = self.bot

        if bot._uptime is not None:
            return

        bot._uptime = datetime.now()

        table_cogs_info = Table(show_edge=False, show_header=False, box=MINIMAL)

        table_cogs_info.add_column(style="blue")
        table_cogs_info.add_column(style="cyan")

        for cog in bot.cogs.values():
            table_cogs_info.add_row(
                cog.__cog_name__,
                f"{docs[:30]}..."
                if len(docs := cog.__cog_description__) > 20
                else docs or "-",
            )

        table_general_info = Table(show_edge=False, show_header=False, box=MINIMAL)

        table_general_info.add_column(style="blue")
        table_general_info.add_column(style="cyan")

        table_general_info.add_row("Prefixes", bot.command_prefix)
        table_general_info.add_row("Default Language", bot.base_lang)
        table_general_info.add_row("python version", platform.python_version())
        table_general_info.add_row("py-cord version", discord.__version__)
        table_general_info.add_row("bot version", bot.__version__)

        table_counts = Table(show_edge=False, show_header=False, box=MINIMAL)

        table_counts.add_column(style="blue")
        table_counts.add_column(style="cyan")

        table_counts.add_row("Servers", str(len(bot.guilds)))
        table_counts.add_row(
            "Unique Users",
            str(len(bot.users)) if bot.intents.members else "-",
        )
        table_counts.add_row("Shards", str(bot.shard_count or "-"))

        self.console.print(
            Columns(
                [
                    Panel(table_cogs_info, title=f"[yellow]cogs - {len(bot.cogs)}"),
                    Panel(table_general_info, title=f"[yellow]{bot.user} login"),
                    Panel(table_counts, title="[yellow]counts"),
                ]
            ),
        )

    @discord.Cog.listener()
    async def on_command(self, ctx: Context):
        self.bot.log.info(
            f"[{ctx.guild.name}] [{ctx.channel.name}] "
            f"{ctx.author} +msg-command+ -> {ctx.command.name}"
        )

    @discord.Cog.listener()
    async def on_application_command(self, ctx: ApplicationContext):
        self.bot.log.info(
            f"[{ctx.guild.name}] [{ctx.channel.name}] "
            f"{ctx.author} +slash-command+ -> {ctx.command.name}"
        )

    @discord.Cog.listener()
    async def on_command_error(self, ctx: Context, error: CommandError):
        if isinstance(error, (CommandNotFound, NotOwner)):
            return

        self.log.exception(type(error).__name__, exc_info=error)

    @discord.Cog.listener()
    async def on_application_command_error(
        self,
        ctx: ApplicationContext,
        error: DiscordException,
    ):
        self.log.exception(type(error).__name__, exc_info=error)


def setup(bot: "Bot"):
    bot.add_cog(BaseEventsCog(bot))
