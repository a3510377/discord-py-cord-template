from datetime import datetime, timedelta

import discord
from discord import Embed

from bot import BaseCog, Bot, ApplicationContext


class InfoCog(BaseCog):
    @discord.slash_command(guild_only=True)
    async def uptime(self, ctx: ApplicationContext):
        _ = ctx._

        uptime: timedelta = datetime.now() - self.bot.uptime

        s = int(uptime.total_seconds())
        days, remainder = divmod(s, (h_s := (s_s := 60) ** 2) * 24)
        hours, remainder = divmod(remainder, h_s)
        minutes, seconds = divmod(remainder, s_s)

        embed = Embed(
            title=_("embed_title"),
            description=_(
                "description_template",
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
            ),
        )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "Bot"):
    bot.add_cog(InfoCog(bot))
