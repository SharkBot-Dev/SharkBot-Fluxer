import asyncio
import os

import aiosqlite
import dotenv

dotenv.load_dotenv()

import fluxer

class SharkBot(fluxer.Bot):
    def __init__(self):
        super().__init__(command_prefix="!.", intents=fluxer.Intents.all())

        self.DB: aiosqlite.Connection = None
        self.CURSUR: aiosqlite.Cursor = None

    async def setup_hook(self):
        self.DB = await aiosqlite.connect("data.db")
        self.CURSUR = await self.DB.cursor()

        await self.CURSUR.execute(
            """
            CREATE TABLE IF NOT EXISTS rolepanels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                emoji_to_roles TEXT NOT NULL
            )
            """
        )

        # Automod
        await self.CURSUR.execute(
            """
            CREATE TABLE IF NOT EXISTS automod (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                automod_id TEXT NOT NULL
            )
            """
        )

        # 警告
        await self.CURSUR.execute(
            """
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                count INTEGER NOT NULL
            )
            """
        )

        # 警告と処罰
        await self.CURSUR.execute(
            """
            CREATE TABLE IF NOT EXISTS punishments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                action TEXT NOT NULL,
                count INTEGER NOT NULL
            )
            """
        )

bot = SharkBot()

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

if __name__ == "__main__":
    asyncio.run(load_extensions())
    bot.run(os.environ.get('TOKEN'))