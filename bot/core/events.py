from datetime import datetime

import discord
from discord import ApplicationContext, DiscordException
from discord.ext.commands import CommandError, CommandNotFound, Context, NotOwner

from bot import BaseCog, Bot


class BaseEventsCog(BaseCog):
    @discord.Cog.listener()
    async def on_ready(self):
        bot = self.bot

        if bot._uptime is not None:
            return

        bot._uptime = datetime.now()
        bot.log.info(f"[cyan]{bot.user}[/cyan]")

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

        self.log.error(error)

    @discord.Cog.listener()
    async def on_application_command_error(
        self,
        ctx: ApplicationContext,
        error: DiscordException,
    ):
        print(f"{type(error)}: {error}")
        print(error.__class__.__name__)


def setup(bot: "Bot"):
    bot.add_cog(BaseEventsCog(bot))
