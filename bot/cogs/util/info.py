from datetime import datetime

import discord
from discord import Embed

from bot import BaseCog, Bot, ApplicationContext


class InfoCog(BaseCog):
    @discord.slash_command(guild_only=True)
    async def uptime(
        self,
        ctx: ApplicationContext,
    ):
        _ = ctx._

        uptime: datetime = datetime.now() - self.bot.uptime
        print(_("description_template"))
        embed = Embed(
            title=_("embed_title"),
            description=uptime.strftime(_("description_template")),
        )

        ctx.respond(embed=embed)


def setup(bot: "Bot"):
    bot.add_cog(InfoCog(bot))
