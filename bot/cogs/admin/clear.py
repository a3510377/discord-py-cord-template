import discord
from discord import Embed, Member, Message

from bot import ApplicationContext, BaseCog, Bot, Translator

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

        reason = ctx._("由 {ctx.author} 清除 - {reason}").format(
            author=ctx.author,
            message=f"{content}..." if len(content) > 10 else content,
            reason=reason or ctx._("無"),
        )

        await message.delete(reason=reason)

        embed = Embed(
            title=ctx._("刪除完畢"),
            description=reason,
        )
        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(guild_only=True)
    @discord.default_permissions(manage_messages=True)
    @discord.option("reason", str, description_localizations="Reason", default=None)
    @discord.option(
        "member",
        Member,
        description_localizations="要刪除的成員訊息",
        default=None,
    )
    @discord.option(
        "count",
        int,
        description_localizations="輸入要刪除的訊息數量",
        min_value=1,
        max_value=512,
    )
    @discord.option(
        "before",
        str,
        description_localizations="刪除這則訊息以前的訊息(請輸入訊息ID)",
        default=None,
    )
    @discord.option(
        "after",
        str,
        description_localizations="刪除以這則訊息以後的訊息(請輸入訊息ID)",
        default=None,
    )
    async def purge(
        self,
        ctx: ApplicationContext,
        count: int,
        reason: str | None,
        member: Member | None,
        before: str | None,
        after: str | None,
    ):
        reason = reason or ctx._("無原因")
        if before and after:
            embed = Embed(
                title=ctx._("錯誤!"),
                description=ctx._("`before` 和 `after` 選項不得同時出現"),
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
            reason=ctx._("由 {ctx.author} 清除 - {reason}").format(
                ctx=ctx,
                reason=reason,
            ),
        )
        embed = Embed(
            title=ctx._("訊息刪除成功!").format(del_message=len(del_message)),
            description=ctx._("原因: {reason}").format(reason=reason),
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "Bot"):
    bot.add_cog(ClearCog(bot))
