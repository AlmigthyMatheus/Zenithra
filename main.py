
import asyncio
import os
import discord
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ext import commands

token = os.environ.get("DISCORD_TOKEN")
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

if token is None:
    print("ERROR: Variável de ambiente DISCORD_TOKEN não encontrada!")
    exit(1)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -b:a 192k'
}
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'http_chunk_size': 10485760
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
            self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
            ))
        else:
            self.sp = None

    async def get_spotify_track_name(self, url):
        if not self.sp:
            return await ctx.send("Configuração do Spotify não encontrada! Verifique as credenciais.")
        try:
            if 'track/' in url:
                track_id = url.split('track/')[1].split('?')[0]
                track = self.sp.track(track_id)
                return f"{track['name']} {track['artists'][0]['name']}"
            return None
        except Exception as e:
            print(f"Erro Spotify: {str(e)}")
            return None

    @commands.command()
    async def play(self, ctx, *, search):
        if not ctx.author.voice:
            return await ctx.send("Você precisa estar em um canal de voz!")

        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()

        await ctx.send("Carregando música...")
        
        # Check if it's a Spotify URL
        if 'spotify.com/track' in search:
            if not self.sp:
                return await ctx.send("Configuração do Spotify não encontrada! Verifique as credenciais.")
            spotify_name = await self.get_spotify_track_name(search)
            if not spotify_name:
                return await ctx.send("Erro ao processar música do Spotify!")
            search = spotify_name

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                if not info.get('entries'):
                    return await ctx.send("Não foi possível encontrar a música!")
                video = info['entries'][0]
                video_info = ydl.extract_info(video['url'], download=False)
                url = video_info['url']
                title = video_info['title']
                self.queue.append((url, title))
                await ctx.send(f"Adicionado à fila: {title}")
            except Exception as e:
                return await ctx.send(f"Erro ao processar a música: {str(e)}")

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
