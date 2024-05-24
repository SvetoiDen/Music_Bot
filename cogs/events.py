import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Бот {self.bot.user} готов к работe')

async def setup(bot):
    await bot.add_cog(Events(bot))