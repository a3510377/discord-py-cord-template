from datetime import datetime
import discord
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
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: discord.DiscordException
    ):
        print(f"{type(error)}: {error}")
        print(error.__class__.__name__)
        # if isinstance(error, MissingPermissions):
        #     embed = discord.Embed(
        #         title="發生錯誤!", description="你沒有權限執行指令", color=0xE74C3C
        #     )
        #     await ctx.respond(embed=embed)


def setup(bot: "Bot"):
    bot.add_cog(BaseEventsCog(bot))
