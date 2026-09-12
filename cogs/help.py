import fluxer

class HelpCog(fluxer.Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

        self.HELP_SESSIONS = []

    def build_embed(self, emoji: str):
        if emoji == "👜":
            embed = fluxer.Embed(title="ロールパネル", description="""`!.rp create <title> <emoji> <role_id>`
ロールパネルを作成します。

`!.rp add <message_id> <emoji> <role_id>`
ロールパネルにロールを追加します。
""")
        else:
            embed = fluxer.Embed(title="SharkBotのヘルプ", description="""`!.help (引数なし)`
このメッセージを表示します。

👜 ロールパネルを作成するコマンドを知ります。
""")

        return embed

    @fluxer.Cog.command(name="help")
    async def help_command(self, msg: fluxer.Message):
        message = await msg.reply(embed=fluxer.Embed(title="SharkBotのヘルプ", description="""
"""))
        self.HELP_SESSIONS.append(message.id)

        await message.add_reaction("🏠")
        await message.add_reaction("👜")

    @fluxer.Cog.listener(name="on_raw_reaction_add")
    async def on_raw_reaction_add_help(self, reaction_info: fluxer.models.reaction.RawReactionActionEvent):
        if reaction_info.message_id not in self.HELP_SESSIONS:
            return

        if reaction_info.user_id == self.bot.user.id:
            return

        emoji = reaction_info.emoji.unicode

        channel = await self.bot.fetch_channel(reaction_info.channel_id)
        message = await channel.fetch_message(reaction_info.message_id)

        embed = self.build_embed(emoji)
        await message.edit(embeds=[embed])

        await message.remove_reaction(reaction_info.emoji, reaction_info.user_id)

async def setup(bot: fluxer.Bot):
    await bot.add_cog(HelpCog(bot))