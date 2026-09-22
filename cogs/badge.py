import fluxer

from fluxer.gateway import GatewayPayload
from fluxer.enums import GatewayOpcode

class BadgeCog(fluxer.Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    async def cog_load(self):
        await self.bot._gateway._send(
            GatewayPayload(
                op=GatewayOpcode.PRESENCE_UPDATE,
                d={
                    "status": "online",
                    "afk": False,
                    "mobile": False,
                    "custom_status": {
                        "text": "!.help / sharkbot.jp"
                    }
                },
            )
        )

async def setup(bot: fluxer.Bot):
    await bot.add_cog(BadgeCog(bot))

async def teardown(bot: fluxer.Bot):
    await bot.remove_cog(BadgeCog(bot).__class__.__name__)