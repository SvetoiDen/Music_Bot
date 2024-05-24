import requests, selenium.webdriver, lxml, asyncio, re, discord, time, os
import ffmpeg
from bs4 import BeautifulSoup as bs
from discord._types import ClientT
from discord.ext import commands
from discord.ext.commands import Context
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from discord import app_commands, Interaction, ui
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import yt_dlp as youtube_dl
from cogs.func_storage.BD_function import BD_Bot

class Modal_get_Music(ui.Modal, title='Трек'):
    track = ui.TextInput(label='Название вашего/их трека/ов',placeholder='(если несколько, то через запятую)', style=discord.TextStyle.short)

    async def on_submit(self, inter: Interaction):
        cur = BD_Bot()
        await inter.response.defer(thinking=True, ephemeral=True)

        tra = str(self.track)
        trs = tra.split(sep=',')

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.use_chromium = True
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0')
        driver = Chrome(options=options)

        count = 0
        for tr in trs:
            count += 1
            searchs = tr.replace(" ", "+")
            driver.get(url=f"https://www.youtube.com/results?search_query={searchs}")
            time.sleep(1.5)
            r = driver.find_element(By.ID, "video-title").get_attribute('href')

            for row in cur.gets_(f"SELECT * FROM music_list WHERE id_user = {inter.user.id}"):
                if not row is None:
                    if row['link_music'] == r:
                        cur.commit_(f"DELETE FROM music_list WHERE link_music = '{r}'")

            cur.commit_(f"INSERT INTO music_list VALUES ({inter.user.id}, '{r}', '{tr}', {count})")

        cur.close_()
        await inter.edit_original_response(content='Ваша музыка была добавлена')

class Button_Edit(ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @ui.button(label=None, emoji='🔄', style=discord.ButtonStyle.primary)
    async def edit_music(self, inter: Interaction, button: ui.Button):
        cur = BD_Bot()
        await inter.response.defer()
        cur.close_()

class Button_Music(ui.View):
    def __init__(self,bot):
        super().__init__()
        self.bot = bot

    @ui.button(label=None, emoji='➕', style=discord.ButtonStyle.green)
    async def get_music(self, inter: Interaction, button: ui.Button):
        await inter.response.send_modal(Modal_get_Music())

    @ui.button(label=None, emoji='▶️', style=discord.ButtonStyle.green)
    async def play(self, inter: Interaction, button: ui.Button):
        cur = BD_Bot()
        await inter.response.send_message(content='Загрузка музыки:▇ 0%', ephemeral=True)

        count = 0
        for row in cur.gets_(f"SELECT * FROM music_list WHERE id_user = {inter.user.id}"):
            if row is None:
                cur.close_()
                return await inter.edit_original_response('У вас нету музыки, которую вы добавляли!')
            else:
                count += 1

        cur.close_()

        await inter.edit_original_response(content='Загрузка музыки:▇ ▇ ▇ 15%')

        vc = await inter.user.voice.channel.connect()
        if vc is None:
            return await inter.edit_original_response(content=f'ОШИБКА! Вы не зашли!')

        async def play_music():
            song_there = os.path.isfile("song.mp3")

            try:
                if song_there:
                    os.remove("song.mp3")
            except PermissionError:
                return

            cur = BD_Bot()
            row = cur.get_(f"SELECT * FROM music_list WHERE id_user = {inter.user.id}")
            url = row['link_music']

            ydl_opts = {
                'format': 'bestaudio/best',
                # 'ffmpeg_location': os.path.realpath('/home//config/ffmpeg/bin/ffmpeg.exe'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            await inter.edit_original_response(content='Загрузка музыки:▇ ▇ ▇ ▇ ▇ ▇ 45%')
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await inter.edit_original_response(content='Загрузка музыки:▇ ▇ ▇ ▇ ▇ ▇ ▇ ▇ 70%')
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "song.mp3")

            await inter.edit_original_response(content='Загрузка музыки:▇ ▇ ▇ ▇ ▇ ▇ ▇ ▇ ▇ ▇ 100%')

            embed = discord.Embed(
                description=f'## Музыка: {row["name_music"]}\n'
                            f'- Заказал: {inter.user.mention}\n'
                            f'- Осталось песен: {count}',
                color=0x3AAACF
            )
            embed.set_author(name='DJ Pikuco', icon_url='https://cdn.discordapp.com/attachments/701876665516687431/1217538911727780000/zJ2-sOdCKdA.jpg?ex=66046479&is=65f1ef79&hm=e808495b112b7909efe397728f46d209f2f08b64d1e5e1668bd3940b8c8c1d3d&')
            embed.set_footer(text='Приятного слушания! P.S если вы добавили еще песни во время проигрования, вам нужно подождать завершения, а затем заново запустить')

            await inter.edit_original_response(content=None, embed=embed)
            # executable = '/config/ffmpeg/bin/ffmpeg.exe'
            vc.play(discord.FFmpegPCMAudio("song.mp3"))
            cur.close_()
            return url

        while count > 0:
            cur = BD_Bot()

            for row in cur.gets_(f"SELECT * FROM music_list WHERE id_user = {inter.user.id}"):
                if not row is None:
                    cur.close_()
                    count -= 1
                    r = await play_music()

                    while vc.is_playing():
                        await asyncio.sleep(.1)

                    cur = BD_Bot()
                    cur.commit_(f"DELETE FROM music_list WHERE link_music = '{r}' AND id_user = {inter.user.id}")
                    cur.close_()

        await vc.disconnect()

    @ui.button(label=None, emoji='🎵', style=discord.ButtonStyle.primary)
    async def list_music_user(self, inter: Interaction, button: ui.Button):
        cur = BD_Bot()

        if not cur.get_(f"SELECT * FROM music_list WHERE id_user = {inter.user.id}") is None:
            embed = discord.Embed(
                title='Ваши добавленные песни',
                color=0x3AAACF
            )
            embed.set_author(name='DJ Pikuco', icon_url='https://cdn.discordapp.com/attachments/701876665516687431/1217538911727780000/zJ2-sOdCKdA.jpg?ex=66046479&is=65f1ef79&hm=e808495b112b7909efe397728f46d209f2f08b64d1e5e1668bd3940b8c8c1d3d&')

            for row in cur.gets_(f"SELECT * FROM music_list WHERE id_user = {inter.user.id} ORDER BY count DESC"):
                embed.add_field(
                    name=f'`{row["count"]}` Песня',
                    value=f'{row["name_music"]}'
                )

            await inter.response.send_message(embed=embed, ephemeral=True, view=Button_Edit(self.bot))
        else:
            await inter.response.send_message(content='У вас нету песен')

        cur.close_()

    @ui.button(label=None, emoji='⏹', style=discord.ButtonStyle.primary)
    async def stop(self, inter: Interaction, button: ui.Button):
        await inter.response.send_message(content='Музыка остановлена',ephemeral=True)

        voice = discord.utils.get(self.bot.voice_clients, guild=inter.guild)
        if voice.is_playing():
            voice.pause()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='музыка')
    @commands.is_owner()
    async def music_embed(self, ctx: Context):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            description='## Музыкальный уголок\n'
                        'Музкальный уголок, где вы можете послушать свои песни одни, или с друзьями. Все песни берутся из ютуба, так что пишите ваши песни понятно и четче.\n'
                        '- ➕ - добавляйте свои песни, либо одну, либо несколько. После этого, можете запускать\n'
                        '- ▶️ - начните проигрывать свои песни, которые вы добавили! *ВНИМАНИЕ: Добавленные песни во время проигрывание не считаются, так что перезапускайте, или останавливайте.*\n'
                        '- ⏹ - Если вы добавили новые песни, или же вы не хотите дальше их слушать, то просто остановите\n'
                        '- 🎵 - просмотрите ваши добавленные песни. Можете что то убрать, изменить их порядок воспроизведения и тд\n',
            color=0xFFD00D
        )
        await ctx.send(embed=embed, view=Button_Music(self.bot))

async def setup(bot):
    await bot.add_cog(Music(bot))