from collections import defaultdict

from discord import Cog, Embed, Interaction, SelectOption, SlashCommand
from discord.ext.commands import Command
from discord.ui import Select, View, select
from discord.utils import async_all

from bot import ApplicationContext, BaseCog, Bot, Context, Translator


_ = Translator(__name__)


class HelpView(View):
    def __init__(self, bot: "Bot") -> None:
        super().__init__(timeout=60)

        self.bot = bot
        self.pages = defaultdict[str, Embed](Embed)
        self.pages_select_options = dict[str, SelectOption]()

    async def setup(self, ctx: ApplicationContext | Context) -> None:
        bot = self.bot

        prefixed_commands: list[Command] = []
        for cmd in bot.application_commands:
            if (
                cmd.guild_only
                and ctx.guild is None
                or not isinstance(cmd, SlashCommand)
            ):
                continue

            if isinstance(ctx, ApplicationContext):
                if (
                    cmd.default_member_permissions is not None
                    and cmd.default_member_permissions > ctx.app_permissions
                ):
                    # check command permissions
                    continue
            else:
                if (
                    cmd.default_member_permissions is not None
                    and cmd.default_member_permissions > ctx.author.guild_permissions
                ):
                    continue

            cog = cmd.cog
            class_name, lang = cog.__class__.__name__, ctx.local()
            if cog:
                cog: Cog
                if isinstance(cog, BaseCog):
                    option = SelectOption(
                        label=cog.__translator_name__.get(lang),
                        description=cog.__translator_description__.get(lang),
                    )
                else:
                    option = SelectOption(
                        label=cog.qualified_name,
                        description=cog.description,
                    )

                option.value = class_name
                self.pages_select_options[class_name] = option
            else:
                continue
                # self.pages_select_options["__utils"] = SelectOption(
                #     label=_("其它雜項"),
                #     value="__utils",
                # )

            self.pages[class_name].add_field(
                name=cmd.mention,
                value=description.get(lang)
                if (description := cmd.description_localizations)
                else "沒有介紹",
            )

        for cmd in bot.prefixed_commands.values():
            if not await async_all(predicate(ctx) for predicate in cmd.checks):
                continue

            prefixed_commands.append(cmd)

        select: Select = self.get_item("__core_help_view_select_help")
        select.options.clear()
        select.options.extend(self.pages_select_options.values())

    @select(custom_id="__core_help_view_select_help")
    async def select_help(self, select: Select, interaction: Interaction):
        id = select.values[0]

        for option in self.pages_select_options.values():
            option.default = False
        self.pages_select_options[id].default = True

        await interaction.response.edit_message(
            embed=self.get_page(id),
            view=self,
        )

    def get_page(self, id: str | None = None) -> Embed:
        if embed := self.pages.get(id, None):
            embed.title = self.pages_select_options[id].label
            embed.description = self.pages_select_options[id].description
        else:
            embed = Embed(title=f"{self.bot.user} 指令列表")
            embed.add_field(name="伺服器數量", value=str(len(self.bot.guilds)))
            embed.add_field(name="機器人延遲", value=f"{self.bot.latency * 1000:.2f} ms")

        self.bot.set_authorization_embed(embed)

        return embed

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.message.edit(
            embed=Embed(title="錯誤", description="超出回應時間"),
            view=self,
        )