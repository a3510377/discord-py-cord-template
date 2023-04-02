import discord
from discord import ApplicationContext, Embed, Member, Message, Option

from bot import BaseCog, Bot, Translator

_ = Translator(__name__)


class ClearCog(BaseCog):
    @discord.slash_command(guild_only=True)
    @discord.default_permissions(manage_messages=True)
    @discord.option(
        "message_id",
        int,
        description_localizations=_("要刪除的訊息 ID", all=True),
    )
    @discord.option(
        "reason",
        str,
        name_localizations=_("原因", all=True),
        description_localizations=_("刪除訊息的原因", all=True),
        default="",
    )
    async def delete(self, ctx: ApplicationContext, message_id: int, reason: str):
        message: Message = await ctx.fetch_message(int(message_id))
        content = ctx.message.content.strip()

        reason = _("{author.name} 刪除了: {msg}\n原因{reason}").format(
            author=ctx.author,
            message=f"{content}..." if len(content) > 10 else content,
            reason=reason,
        )

        await message.delete(
            reason=_("delete_reason_template").format(
                ctx=ctx,
                reason=reason,
            )
        )

        embed = Embed(
            title=_("刪除完畢"),
            description=reason,
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
            reason=_("delete_reason_template").format(
                ctx=ctx,
                reason=reason,
            ),
        )
        embed = Embed(
            title=_("done").format(del_message=len(del_message)),
            description=_("embed_description").format(reason=reason),
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "Bot"):
    bot.add_cog(ClearCog(bot))
