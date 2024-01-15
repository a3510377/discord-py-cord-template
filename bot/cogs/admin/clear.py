import discord
from discord import Embed, Member, Message

from bot import ApplicationContext, BaseCog, Bot, Translator, cog_i18n

_ = Translator(__name__)


@cog_i18n
class ClearCog(BaseCog, name="管理"):
    @discord.slash_command(
        guild_only=True,
        i18n_name=_("刪除"),
        i18n_description=_("刪除一個訊息"),
    )
    @discord.default_permissions(manage_messages=True)
    @discord.option(
        "message_id",
        str,
        i18n_name=_("訊息id"),
        i18n_description=_("要刪除的訊息 ID"),
    )
    @discord.option(
        "reason",
        str,
        i18n_name=_("原因"),
        i18n_description=_("刪除訊息的原因"),
        default="",
    )
    async def delete(self, ctx: ApplicationContext, message_id: str, reason: str):
        message: Message = await ctx.fetch_message(int(message_id))
        content = message.content.strip()
        author = ctx.author

        await message.delete(
            reason=ctx._("由 {ctx.author} 清除 - {reason}", guild_local=True).format(
                ctx=ctx,
                message=f"{content}..." if len(content) > 10 else content,
                reason=reason or ctx._("無原因", guild_local=True),
            )
        )

        embed = Embed(
            title=ctx._("刪除完畢"),
            description=reason,
        )
        embed.set_author(
            name=author,
            icon_url=author.avatar.url if author.avatar.url else None,
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(
        guild_only=True,
        i18n_name=_("批量刪除"),
        i18n_description=_("刪除大量訊息"),
    )
    @discord.default_permissions(manage_messages=True)
    @discord.option(
        "reason",
        str,
        i18n_name=_("原因"),
        i18n_description=_("原因"),
        default=None,
    )
    @discord.option(
        "member",
        Member,
        i18n_name=_("成員"),
        i18n_description=_("要刪除的成員訊息"),
        default=None,
    )
    @discord.option(
        "count",
        int,
        i18n_name=_("數量"),
        i18n_description=_("輸入要刪除的訊息數量"),
        min_value=1,
        max_value=512,
    )
    @discord.option(
        "before",
        str,
        i18n_name=_("以前"),
        i18n_description=_("刪除這則訊息以前的訊息(請輸入訊息ID)"),
        default=None,
    )
    @discord.option(
        "after",
        str,
        i18n_name=_("之後"),
        i18n_description=_("刪除以這則訊息以後的訊息(請輸入訊息ID)"),
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
            reason=ctx._("由 {ctx.author} 清除 - {reason}", guild_local=True).format(
                ctx=ctx,
                reason=ctx._("原因: {reason}", guild_local=True),
            ),
        )
        embed = Embed(
            title=ctx._("訊息刪除成功!").format(del_message=len(del_message)),
            description=ctx._("原因: {reason}").format(reason=reason),
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "Bot"):
    bot.add_cog(ClearCog(bot))
