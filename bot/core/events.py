import discord
from discord import ApplicationContext, DiscordException
from datetime import datetime

from bot import BaseCog, Bot


class BaseEventsCog(BaseCog):
    @discord.Cog.listener()
    async def on_ready(self):
        bot = self.bot

        if bot._uptime is not None:
            return

        bot._uptime = datetime.utcnow()
        bot.log.info(f"[cyan]{bot.user}[/cyan]")

    @discord.Cog.listener()
    async def on_application_command(self, ctx: ApplicationContext):
        self.bot.log.info(
            f"[{ctx.guild.name}] [{ctx.channel.name}] "
            f"{ctx.author} -> {ctx.command.name}"
        )

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
