import json

import fluxer

class PanelCog(fluxer.Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    @fluxer.Cog.command(name="rp")
    @fluxer.has_permission(fluxer.Permissions.MANAGE_ROLES)
    async def role_panel(self, msg: fluxer.Message):
        split_message = msg.content.split()
        if len(split_message) < 4:
            await msg.reply("使用方法:\n`!.rp create <title> <emoji> <role_id>`\n`!.rp add <message_id> <emoji> <role_id>`")
            return

        sub_command_name = split_message[1]
        if sub_command_name == "create":
            title = split_message[2]
            emoji = split_message[3]
            role_id = split_message[4]
            try:
                message = await msg.channel.send(embed=fluxer.Embed(title=title, description=f"{emoji} <@&{role_id}>"))
                await message.add_reaction(emoji)
            except Exception as e:
                await msg.reply("エラー！")
                return

            await self.bot.CURSUR.execute("INSERT INTO rolepanels (channel_id, message_id, emoji_to_roles) VALUES (?, ?, ?)", (str(msg.channel_id), str(message.id), json.dumps({emoji: role_id})))
            await self.bot.DB.commit()
        elif sub_command_name == "add":
            message_id = split_message[2]
            await self.bot.CURSUR.execute("SELECT channel_id, message_id, emoji_to_roles FROM rolepanels WHERE channel_id = ? AND message_id = ?", (str(msg.channel_id), str(message_id),))
            setting = await self.bot.CURSUR.fetchone()
            if not setting:
                await msg.reply("不明なロールパネルです。\n`!.rp create`コマンドで作に作成してください。")
                return

            try:
                role_id = split_message[4]
                message = await msg.channel.fetch_message(int(message_id))
                emoji = split_message[3]
                embed = message.embeds[0].copy()
                embed["description"] += f"\n{emoji} <@&{role_id}>"
                await message.edit(embeds=[embed])
                await message.add_reaction(emoji)
            except Exception as e:
                print(e)
                return

            emoji_to_role_id = json.loads(setting[2])
            emoji_to_role_id[emoji] = role_id

            await self.bot.CURSUR.execute("UPDATE rolepanels SET emoji_to_roles = ? WHERE message_id = ?", (json.dumps(emoji_to_role_id), str(message.id)))
            await self.bot.DB.commit()

    @fluxer.Cog.listener(name="on_raw_reaction_add")
    async def on_raw_reaction_add_rp(self, reaction_info: fluxer.models.reaction.RawReactionActionEvent):
        # print(reaction_info)

        await self.bot.CURSUR.execute("SELECT channel_id, message_id, emoji_to_roles FROM rolepanels WHERE channel_id = ? AND message_id = ?", (str(reaction_info.channel_id), str(reaction_info.message_id),))
        setting = await self.bot.CURSUR.fetchone()

        # print(setting)

        if not setting:
            return

        if reaction_info.user_id == self.bot.user.id:
            return

        guild_id = str(reaction_info.guild_id)
        user_id = str(reaction_info.user_id)
        if reaction_info.emoji.is_unicode_emoji:
            emoji = str(reaction_info.emoji.unicode)
        else:
            emoji = str(reaction_info.emoji.id)

        guild = self.bot.get_guild(int(guild_id))
        member = await guild.fetch_member(int(user_id))
        roles = await guild.fetch_roles()

        emoji_to_roles = json.loads(setting[2])
        # print(emoji_to_roles)
        # print(emoji)
        emoji_to_role = emoji_to_roles.get(emoji)
        # print(emoji_to_role)
        for r in roles:

            if str(r.id) == emoji_to_role:
                if member.has_role(r.id):
                    await member.remove_role(r.id)
                else:
                    await member.add_role(r.id)
                channel = await self.bot.fetch_channel(reaction_info.channel_id)
                message = await channel.fetch_message(reaction_info.message_id)
                await message.remove_reaction(emoji, reaction_info.user_id)
                return

async def setup(bot: fluxer.Bot):
    await bot.add_cog(PanelCog(bot))

async def teardown(bot: fluxer.Bot):
    await bot.remove_cog(PanelCog(bot).__class__.__name__)