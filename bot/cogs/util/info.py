from datetime import datetime, timedelta

import discord
from discord import ApplicationContext, Embed

from bot import BaseCog, Bot, Translator

_ = Translator(__name__)


class InfoCog(BaseCog):
    @discord.slash_command(
        guild_only=True,
        name_localizations=_("上線時間", all=True),
        description_localizations=_("查看機器人上線時間", all=True),
    )
    async def uptime(self, ctx: ApplicationContext):
        uptime: timedelta = datetime.now() - self.bot.uptime

        s = int(uptime.total_seconds())
        days, remainder = divmod(s, (h_s := (s_s := 60) ** 2) * 24)
        hours, remainder = divmod(remainder, h_s)
        minutes, seconds = divmod(remainder, s_s)

        embed = Embed(
            title=_("機器人上線時間"),
            description=_(
                "{days:02d}天 {hours:02d}小時 {minutes:02d}分鐘 {seconds:02d}秒",
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
            ),
        )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "Bot"):
    bot.add_cog(InfoCog(bot))
