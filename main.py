
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
            return None
        try:
            if 'track/' in url:
                track_id = url.split('track/')[1].split('?')[0]
                track = self.sp.track(track_id)
                return f"{track['name']} {track['artists'][0]['name']}"
            elif 'playlist/' in url:
                playlist_id = url.split('playlist/')[1].split('?')[0]
                playlist = self.sp.playlist_tracks(playlist_id)
                tracks = []
                for item in playlist['items']:
                    track = item['track']
                    tracks.append(f"{track['name']} {track['artists'][0]['name']}")
                return tracks
            return None
        except Exception as e:
            print(f"Erro Spotify: {str(e)}")
            return None

    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Comandos do Bot",
            description="Lista de comandos disponíveis:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="!play [música/URL]",
            value="Toca uma música do YouTube ou Spotify",
            inline=False
        )
        embed.add_field(
            name="!skip",
            value="Pula a música atual",
            inline=False
        )
        embed.add_field(
            name="!pause",
            value="Pausa a música atual",
            inline=False
        )
        embed.add_field(
            name="!resume",
            value="Continua a música pausada",
            inline=False
        )
        embed.add_field(
            name="!stop",
            value="Para a música e limpa a fila",
            inline=False
        )
        embed.add_field(
            name="!queue",
            value="Mostra a fila de músicas",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def play(self, ctx, *, search):
        if not ctx.author.voice:
            return await ctx.send("Você precisa estar em um canal de voz!")

        try:
            channel = ctx.author.voice.channel
            try:
                if ctx.voice_client is None:
                    await channel.connect(timeout=20, reconnect=True)
                elif ctx.voice_client.is_connected():
                    await ctx.voice_client.move_to(channel)
                
                if not ctx.voice_client or not ctx.voice_client.is_connected():
                    await asyncio.sleep(1)
                    await channel.connect(timeout=20, reconnect=True)
                
                if not ctx.voice_client or not ctx.voice_client.is_connected():
                    return await ctx.send("Não foi possível conectar ao canal de voz!")
                
            except discord.ClientException as e:
                print(f"Erro de conexão: {e}")
                if ctx.voice_client:
                    await ctx.voice_client.disconnect()
                await asyncio.sleep(1)
                await channel.connect(timeout=20, reconnect=True)

            await ctx.send("Carregando música...")
        
        # Check if it's a Spotify URL
        if 'spotify.com' in search:
            if not self.sp:
                return await ctx.send("Configuração do Spotify não encontrada! Verifique as credenciais do Spotify.")
            if not (SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET):
                return await ctx.send("Credenciais do Spotify não configuradas!")
            
            try:
                spotify_name = await self.get_spotify_track_name(search)
                if not spotify_name:
                    return await ctx.send("Música do Spotify não encontrada!")
                
                if isinstance(spotify_name, list):
                    # É uma playlist
                    await ctx.send(f"Adicionando {len(spotify_name)} músicas da playlist...")
                    for track_name in spotify_name:
                        self.queue.append((None, track_name))
                    await self.play_next(ctx)
                    return
                else:
                    # É uma música única
                    search = spotify_name
            except Exception as e:
                print(f"Erro Spotify: {str(e)}")
                return await ctx.send("Erro ao processar música do Spotify! Verifique se o link está correto.")

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
        try:
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                return
                
            if self.queue:
                url, title = self.queue.pop(0)
                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                await ctx.send(f"Tocando agora: {title}")
            else:
                await ctx.send("A fila está vazia!")
        except Exception as e:
            print(f"Erro ao tocar próxima música: {str(e)}")
            await ctx.send("Ocorreu um erro ao tocar a música!")

    @commands.command(aliases=['SKIP'])
    async def skip(self, ctx):
        if ctx.voice_client:
            if ctx.voice_client.is_playing():
                await ctx.send("Música pulada!")
                ctx.voice_client.stop()
            else:
                await ctx.send("Não há música tocando!")

    @commands.command(aliases=['PAUSE'])
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Música pausada!")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Música continuando!")

    @commands.command(aliases=['STOP'])
    async def stop(self, ctx):
        if ctx.voice_client:
            try:
                self.queue.clear()
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                if ctx.voice_client.is_connected():
                    await ctx.voice_client.disconnect(force=True)
                await ctx.send("Música parada e fila limpa!")
            except Exception as e:
                print(f"Erro ao parar música: {e}")
                await ctx.send("Erro ao parar música!")

    @commands.command()
    async def queue(self, ctx):
        if not self.queue:
            await ctx.send("A fila está vazia!")
            return
            
        embed = discord.Embed(title="Fila de Músicas", color=discord.Color.blue())
        for i, (_, title) in enumerate(self.queue, 1):
            embed.add_field(name=f"{i}. ", value=title, inline=False)
        await ctx.send(embed=embed)

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(Music(self))

    async def on_ready(self):
        print(f"Bot conectado como {self.user}")

intents = discord.Intents.default()
intents.message_content = True

bot = MyBot(command_prefix='!', intents=intents)
bot.run(token)
