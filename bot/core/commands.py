# import discord
# from discord import ApplicationContext, DiscordException
# from datetime import datetime

from bot import BaseCog, Bot


class BaseCommandsCog(BaseCog):
    ...


def setup(bot: "Bot"):
    bot.add_cog(BaseCommandsCog(bot))
