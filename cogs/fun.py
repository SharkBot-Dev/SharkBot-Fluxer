import json

import aiohttp
import fluxer
import urllib.parse

class FunCog(fluxer.Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    @fluxer.Cog.command(name="fox")
    async def fox_command(self, msg: fluxer.Message):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://randomfox.ca/floof/") as fox:
                await msg.reply(embed=fluxer.Embed(title="生成しました。").set_image(url=json.loads(await fox.text())['image']))

    @fluxer.Cog.command(name="choyen")
    async def choyen_command(self, msg: fluxer.Message):
        split_message = msg.content.split()
        if len(split_message) < 3:
            await msg.reply("使用方法:\n`!.choyen <top> <down>`")
            return

        def make_5000(up: str, down: str, noa: bool = None, rainbow: bool = False):
            text = f"https://gsapi.cbrx.io/image?top={urllib.parse.quote(up)}&bottom={urllib.parse.quote(down)}&type=png"
            if noa:
                text += "&noalpha=true"
            if rainbow:
                text += "&rainbow=true"
            return text

        await msg.reply(embed=fluxer.Embed(title="生成しました。").set_image(url=make_5000(split_message[1], split_message[2])))

async def setup(bot: fluxer.Bot):
    await bot.add_cog(FunCog(bot))

async def teardown(bot: fluxer.Bot):
    await bot.remove_cog(FunCog(bot).__class__.__name__)