import json
import re

import fluxer

class AutoModCog(fluxer.Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

        self.AUTOMOD_IDS = ["invite"]
        self.ACTION_IDS = ["none", "send_message"]
        self.INVITE_RE = re.compile(r"fluxer\.gg/.+")

    @fluxer.Cog.command(name="automod")
    @fluxer.has_permission(fluxer.Permissions.MANAGE_GUILD)
    async def automod(self, msg: fluxer.Message):
        split_message = msg.content.split()
        if len(split_message) < 2:
            await msg.reply("使用方法:\n`!.automod create <automod_id>`\n`!.automod delete <automod_id>`\n`!.automod punishment <count> <action>`\n`!.automod punishments`\n\nAutoModのID一覧: invite")
            return

        sub_command_name = split_message[1]
        
        if sub_command_name == "create":
            automod_id = split_message[2]
            if automod_id not in self.AUTOMOD_IDS:
                automod_list_text = ", ".join(self.AUTOMOD_IDS)
                await msg.reply(f"不正なAutoModのIDです。\n使用方法なID一覧: {automod_list_text}")
                return

            await self.bot.CURSUR.execute("SELECT guild_id, automod_id FROM automod WHERE guild_id = ? AND automod_id = ?", (str(msg.guild_id), str(automod_id),))
            setting = await self.bot.CURSUR.fetchone()

            if setting:
                await msg.reply(f"そのAutoModはすでに有効です。")
                return

            await self.bot.CURSUR.execute("INSERT INTO automod (guild_id, automod_id) VALUES (?, ?)", (str(msg.guild_id), automod_id))
            await self.bot.DB.commit()

            await msg.reply(f"「{automod_id}」というAutoModを有効にしました。")
        elif sub_command_name == "delete":
            automod_id = split_message[2]
            if automod_id not in self.AUTOMOD_IDS:
                automod_list_text = ", ".join(self.AUTOMOD_IDS)
                await msg.reply(f"不正なAutoModのIDです。\n使用方法なID一覧: {automod_list_text}")
                return

            await self.bot.CURSUR.execute("SELECT guild_id, automod_id FROM automod WHERE guild_id = ? AND automod_id = ?", (str(msg.guild_id), str(automod_id),))
            setting = await self.bot.CURSUR.fetchone()

            if not setting:
                await msg.reply(f"そのAutoModはすでに無効です。")
                return

            await self.bot.CURSUR.execute("DELETE FROM automod WHERE guild_id = ? AND automod_id = ?", (str(msg.guild_id), automod_id,))
            await self.bot.DB.commit()

            await msg.reply(f"「{automod_id}」というAutoModを無効にしました。")
        elif sub_command_name == "punishment":
            count = split_message[2]
            try:
                count = int(count)
            except ValueError:
                await msg.reply("不正な数字です。")
                return

            action = split_message[3]
            if action not in self.ACTION_IDS:
                action_list_text = ", ".join(self.ACTION_IDS)
                await msg.reply(f"不正なアクションIDです。\n使用方法なID一覧: {action_list_text}")
                return

            await self.bot.CURSUR.execute("SELECT count, action, guild_id FROM punishments WHERE guild_id = ? AND count = ?", (str(msg.guild_id), count,))
            setting = await self.bot.CURSUR.fetchone()

            if not setting:
                await self.bot.CURSUR.execute("INSERT INTO punishments (count, action, guild_id) VALUES (?, ?, ?)", (count, action, str(msg.guild_id)))
                await self.bot.DB.commit()
            else:
                await self.bot.CURSUR.execute("UPDATE punishments SET action = ? WHERE guild_id = ? AND count = ?", (action, str(msg.guild_id), count,))
                await self.bot.DB.commit()

            await msg.reply(f"{count}回目の警告で、{action}を実行するようにしました。")
        elif sub_command_name == "punishments":
            await self.bot.CURSUR.execute("SELECT count, action, guild_id FROM punishments WHERE guild_id = ?", (str(msg.guild_id),))
            rows = await self.bot.CURSUR.fetchall()
            text = ""
            for r in sorted(rows):
                if r[1] == "none":
                    continue
                text += f"{r[0]}回目: {r[1]}\n"
            await msg.reply(embed=fluxer.Embed(description=text, title="何回目の警告で何をするか"))

    @fluxer.Cog.command(name="clear_warn")
    @fluxer.has_permission(fluxer.Permissions.MANAGE_GUILD)
    async def clear_warn(self, msg: fluxer.Message):
        split_message = msg.content.split()
        if len(split_message) != 2:
            await msg.reply("使用方法: `!.clear_warn <user_id>`")
            return
        try:
            user_id = int(split_message[1])
            user = await msg.guild.fetch_member(user_id)

            if not user:
                await msg.reply("不明なユーザーIDです。")
                return
        except:
            await msg.reply("不明なユーザーIDです。")
            return

        await self.bot.CURSUR.execute("SELECT count, guild_id, user_id FROM warns WHERE guild_id = ? AND user_id = ?", (str(msg.guild_id), str(user.user.id),))
        setting = await self.bot.CURSUR.fetchone()
        count = 0
        if not setting:
            await self.bot.CURSUR.execute("INSERT INTO warns (guild_id, user_id, count) VALUES (?, ?, ?)", (str(msg.guild_id), str(user.user.id), count,))
            await self.bot.DB.commit()
        else:
            await self.bot.CURSUR.execute("UPDATE warns SET count = ? WHERE guild_id = ? AND user_id = ?", (count, str(msg.guild_id), str(user.user.id),))
            await self.bot.DB.commit()
        await msg.reply(f"{user.user.display_name} の警告を削除しました。")        

    async def warn(self, guild_id: str, user_id: str):
        await self.bot.CURSUR.execute("SELECT count, guild_id, user_id FROM warns WHERE guild_id = ? AND user_id = ?", (str(guild_id), str(user_id),))
        setting = await self.bot.CURSUR.fetchone()
        count = 1
        if not setting:
            await self.bot.CURSUR.execute("INSERT INTO warns (guild_id, user_id, count) VALUES (?, ?, ?)", (str(guild_id), str(user_id), count,))
            await self.bot.DB.commit()
        else:
            count = setting[0] + 1
            await self.bot.CURSUR.execute("UPDATE warns SET count = ? WHERE guild_id = ? AND user_id = ?", (count, str(guild_id), str(user_id),))
            await self.bot.DB.commit()

        return count

    async def execute_punishment_message(self, message: fluxer.Message, action: str, memo: str, count: int):
        if action == "send_message":
            await message.channel.send(embed=fluxer.Embed(description=f"{message.author.mention}が{memo}ため、処罰されました。\n\nこれは{count}回目の警告です。"))

    @fluxer.Cog.listener(name="on_message")
    async def on_message_automod(self, message: fluxer.Message):
        if message.author.id == self.bot.user.id:
            return

        await self.bot.CURSUR.execute("SELECT guild_id, automod_id FROM automod WHERE guild_id = ? AND automod_id = ?", (str(message.guild_id), str("invite"),))
        setting = await self.bot.CURSUR.fetchone()
        if not setting:
            return

        check = self.INVITE_RE.search(message.content)
        if check:
            await message.delete()

            count = await self.warn(str(message.guild_id), str(message.author.id))

            await self.bot.CURSUR.execute("SELECT count, action, guild_id FROM punishments WHERE guild_id = ? AND count = ?", (str(message.guild_id), count,))
            setting = await self.bot.CURSUR.fetchone()
            if not setting:
                return

            await self.execute_punishment_message(message, setting[1], "招待リンクを送信した", count)

async def setup(bot: fluxer.Bot):
    await bot.add_cog(AutoModCog(bot))

async def teardown(bot: fluxer.Bot):
    await bot.remove_cog(AutoModCog(bot).__class__.__name__)