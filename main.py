
import asyncio
import os
import discord
import yt_dlp
from discord.ext import commands

token = os.environ.get("DISCORD_TOKEN")
if token is None:
    print("ERROR: Variável de ambiente DISCORD_TOKEN não encontrada!")
    exit(1)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.command()
    async def play(self, ctx, *, search):
        if not ctx.author.voice:
            return await ctx.send("Você precisa estar em um canal de voz!")

        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()

        await ctx.send("Carregando música...")
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['formats'][0]['url']
            title = info['title']
            self.queue.append((url, title))
            await ctx.send(f"Adicionado à fila: {title}")

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
            await ctx.send(f"Tocando agora: {title}")
        else:
            await ctx.send("A fila está vazia!")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Música pulada!")

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(Music(self))

    async def on_ready(self):
        print(f"Bot conectado como {self.user}")

intents = discord.Intents.default()
intents.message_content = True

bot = MyBot(command_prefix='!', intents=intents)
bot.run(token)
