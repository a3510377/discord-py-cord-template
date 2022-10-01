import inspect

from discord.ext import commands

from bot import BaseCog, Bot, ApplicationContext
from bot.utils.util import get_absolute_name_from_path


class BaseCommandsCog(BaseCog):
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: ApplicationContext):
        bot = self.bot
        errors = []
        cogs = [
            get_absolute_name_from_path(inspect.getfile(cog.__class__))
            for cog in bot.cogs.values()
        ]

        cogs.remove(command_el := "bot.core.commands")

        for name in cogs:
            try:
                bot.reload_extension(name)
            except Exception as e:
                errors.append(e)

        bot.reload_extension(command_el)

        await ctx.send(
            "reload all"
            + (f"\n```{error_str}```" if (error_str := "\n".join(errors)) else "")
        )


def setup(bot: "Bot"):
    bot.add_cog(BaseCommandsCog(bot))
