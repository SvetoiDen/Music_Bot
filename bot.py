import os
import discord
from discord.ext import commands
import config.config
from cogs.music import Button_Music

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('$'), help_command=None, intents=discord.Intents.default().all())

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

bot = Bot()

@bot.event
async def on_ready():
    channel_4 = bot.get_channel(1235738984169209897)
    embed = discord.Embed(
        description='## Музыкальный уголок\n'
                    'Музкальный уголок, где вы можете послушать свои песни одни, или с друзьями. Все песни берутся из ютуба, так что пишите ваши песни понятно и четче.\n'
                    '- ➕ - добавляйте свои песни, либо одну, либо несколько. После этого, можете запускать\n'
                    '- ▶️ - начните проигрывать свои песни, которые вы добавили! *ВНИМАНИЕ: Добавленные песни во время проигрывание не считаются, так что перезапускайте, или останавливайте.*\n'
                    '- ⏹ - Если вы добавили новые песни, или же вы не хотите дальше их слушать, то просто остановите\n'
                    '- 🎵 - просмотрите ваши добавленные песни. Можете что то убрать, изменить их порядок воспроизведения и тд\n',
        color=0xFFD00D
    )

    await channel_4.purge(limit=1)
    await channel_4.send(embed=embed, view=Button_Music(bot))

bot.run(config.config.TOKEN)
