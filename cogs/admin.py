import fluxer
import os

class AdminCog(fluxer.Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    @fluxer.Cog.command(name="reload")
    async def admin_reload_command(self, msg: fluxer.Message):
        if str(msg.author.id) != os.environ.get('OWNER_ID'):
            await msg.reply("権限がありません。")
            return
        split_message = msg.content.split()
        if len(split_message) != 2:
            await msg.reply("使用方法: !.reload <cog_name>")
            return

        cog_name = split_message[1]
        await self.bot.reload_extension("cogs." + cog_name)

        await msg.reply("リロード完了。")

    @fluxer.Cog.command(name="load")
    async def admin_load_command(self, msg: fluxer.Message):
        if str(msg.author.id) != os.environ.get('OWNER_ID'):
            await msg.reply("権限がありません。")
            return
        split_message = msg.content.split()
        if len(split_message) != 2:
            await msg.reply("使用方法: !.load <cog_name>")
            return

        cog_name = split_message[1]
        await self.bot.load_extension("cogs." + cog_name)

        await msg.reply("リロード完了。")

async def setup(bot: fluxer.Bot):
    await bot.add_cog(AdminCog(bot))