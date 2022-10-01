import discord
from discord import Embed, Option, Message, Member

from bot import BaseCog, Bot, ApplicationContext


class ClearCog(BaseCog):
    @discord.slash_command(guild_only=True)
    @discord.default_permissions(manage_messages=True)
    async def delete(
        self,
        ctx: ApplicationContext,
        message_id: Option(str, "輸入要刪除的訊息ID"),
        reason: Option(str, "Reason", default=None),
    ):
        _ = ctx._
        reason = reason or _("default_reason")
        message: Message = await ctx.fetch_message(int(message_id))

        await message.delete(
            reason=_(
                "delete_reason_template",
                ctx=ctx,
                reason=reason,
            )
        )

        embed = Embed(
            title=_("done"),
            description=_("embed_description", reason=reason),
        )
        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(guild_only=True)
    @discord.default_permissions(manage_messages=True)
    async def purge(
        self,
        ctx: ApplicationContext,
        count: Option(int, "輸入要刪除的訊息數量", min_value=1, max_value=512),
        reason: Option(str, "Reason", default=None),
        member: Option(Member, "要刪除的成員訊息", default=None),
        before: Option(str, "刪除這則訊息以前的訊息(請輸入訊息ID)", default=None),
        after: Option(str, "刪除以這則訊息以後的訊息(請輸入訊息ID)", default=None),
    ):
        _ = ctx._
        reason = reason or _("default_reason")
        if before and after:
            embed = Embed(
                title=_("error"),
                description=_("before_after_error"),
                color=0xE74C3C,
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        elif before:
            before: Message = await ctx.fetch_message(int(before))
        elif after:
            after: Message = await ctx.fetch_message(int(after))

        del_message = await ctx.channel.purge(
            limit=count,
            check=lambda msg: msg.author == member or not member,
            before=before,
            after=after,
            reason=_(
                "delete_reason_template",
                ctx=ctx,
                reason=reason,
            ),
        )
        embed = Embed(
            title=_("done", del_message=len(del_message)),
            description=_("embed_description", reason=reason),
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "Bot"):
    bot.add_cog(ClearCog(bot))
