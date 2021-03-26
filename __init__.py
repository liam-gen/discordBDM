import discord
import discord.ext
from discord.ext import commands
import DiscordUtils
import random
import os
import asyncio
import youtube_dl

from webserver import keep_alive

def bot(prefix, description, token, status, color, chjoinremove):
    botprefix = prefix
    botdescription = description
    bottoken = token
    botstatus = status
    botcolor = color
    botjoinch = chjoinremove

    default_intents = discord.Intents.default()
    default_intents.members = True

    client = commands.Bot(command_prefix=botprefix, description=botdescription, intents=default_intents)

    musics = {}

    ytdl = youtube_dl.YoutubeDL()

    class Video:
        def __init__(self, link):
            video = ytdl.extract_info(link, download=False)
            video_format = video["formats"] [0]
            self.url = video["webpage_url"]
            self.stream_url = video_format["url"]


    
    @client.event
    async def on_ready():
        print(
            f"Le bot {client.user.name} a été lancé ! \nStatistiques \nVersion : 0.0.2\nServeurs : {len(client.guilds)}\n\n----------\n\nChargement ...\nStatus : {botstatus}\nPréfix : {botprefix}\nDescription : {botdescription}\n\n----------\n\nToutes les commandes sont lancés !\nLancement du cog 1 ..\nCog 1 chargé avec succès !\nChargement des commandes musiques ...\n\n----------\n\nCommandes de musiques opérationelles !"
        )
        await client.change_presence(activity=discord.Game(name=botstatus))

    @client.command()
    async def ping(ctx):
        latence = client.latency * 1000
        await ctx.send(f"Pong , je t'ai répondu en {round(latence)}ms !")

    @client.command()
    @commands.has_permissions(kick_members=True)
    async def kick(ctx, member: discord.Member, reason=None):
        try:
            await member.kick(reason=f"Kick par {ctx.author.name} - {client.user.name} Mod - Raison :" + reason)
            embed = discord.Embed(title="Une nouvelle expulsion !", description=f"Oust **{member.name}** ! Il a été expluser par **{ctx.author.name}**!", colour=botcolor)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Une erreur s'est produite")

    @client.remove_command("help")
    @client.command()
    async def help(ctx):
        embed1 = discord.Embed(title="Page d'aide 0/4",
                              description="Sommaire :\n\nPage 1 : Bot\nPage 2 : Modération\nPage 3 : Informations\nPage 4 : Musique",
                              colour=botcolor)
        embed2 = discord.Embed(title="Page d'aide 1/4 - Bot", description=f"**Commandes**\n\n`{botprefix}ping`\n`{botprefix}discordBMD`", colour=botcolor)
        embed3 = discord.Embed(title="Page 2/4 - Modération", description=f"**Commandes**\n\n`{botprefix}kick`", colour=botcolor)
        embed4 = discord.Embed(title="Page 3/4 - Informations", description=f"**Commandes**\n\n`{botprefix}serveurinfo`", colour=botcolor)
        embed5 = discord.Embed(title="Page d'aide 4/4 - Musique", description=f"**Commandes**\n\n`{botprefix}join`\n`{botprefix}play`\n`{botprefix}pause`\n`{botprefix}resume`\n`{botprefix}stop`", colour=botcolor)
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
        paginator.add_reaction("⬅️", "back")
        paginator.add_reaction("🔴", "lock")
        paginator.add_reaction("➡️", "next")
        embeds = [embed1, embed2, embed3, embed4, embed5]
        await paginator.run(embeds)

    @client.command(aliases=['BMD', 'bmd'])
    async def discordBMD(ctx):
        embed = discord.Embed(title="DiscordBMD", description="Github : [Clique ici](https://github.com/liam-gen/discordBDM)", colour=botcolor)
        embed.set_footer(text="Pour télécharger la package, rend toi sur le github")
        await ctx.send(embed=embed)

    @client.event
    async def on_member_join(member):
        channel = member.guild.get_channel(id=botjoinch)
        await channel.send(f"Bienvenue a **{member.display_name}** sur {member.guild.name} !")

    @client.event
    async def on_member_remove(member):
        channel = member.guild.get_channel(botjoinch)
        await channel.send(f"Au revoir a **{member.display_name}** :sob: !")


    @client.command(aliases=["si"])
    async def serveurinfo(ctx):
        server = ctx.guild
        id = server.id
        nbtext = len(server.text_channels)
        nbvoice = len(server.voice_channels)
        nbmember = server.member_count
        name = server.name
        embed = discord.Embed(title=f"Serveur Info {name}", description=f"Membres : {nbmember}\nSalons textuels : {nbtext}\nSalons vocaux : {nbvoice}\nId : {id}", colour=botcolor)
        await ctx.send(embed=embed)

    @client.command()
    async def skip(ctx):
        client = ctx.guild.voice_client
        client.stop()
        message = await ctx.send("Je passe à la musique suivante ! ")
        await message.add_reaction("⏭️")

    @client.command()
    async def pause(ctx):
        client = ctx.guild.voice_client
        if not client.is_paused():
            client.pause()
            message = await ctx.send("Hmmm j'ai bien mérité une pause !")
            await message.add_reaction("⏸")

    @client.command()
    async def stop(ctx):
        client = ctx.guild.voice_client

        await client.disconnect()
        message = await ctx.send("Quoi ?! Ma musique n'était pas bien ?")
        await message.add_reaction("🛑")
        musics[ctx.guild] = []



    @client.command()
    async def resume(ctx):
        client = ctx.guild.voice_client

        if client.is_paused:
            client.resume()
            message = await ctx.send("Bon, je dois reprendre :sob:")
            await message.add_reaction("▶")
    def play_song(client, queue,  song):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

        def next(_):

            if len(queue) > 0:
                new_song = queue[0]
                del queue[0]
                play_song(client, queue, new_song)
                

            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(), client.loop)
           
        client.play(source, after=next)
    @client.command()
    async def play(ctx, url):
        print(f"{ctx.author.name} a lancé une musique sur {ctx.guild} !")
        client = ctx.guild.voice_client

        if client and client.channel:
            video = Video(url)
            musics[ctx.guild].append(video)
            message = await ctx.send(f"J'ajoute {video.url} a la queue !")
            await message.add_reaction("➕")
        else:

            channel = ctx.author.voice.channel

            video = Video(url)
            musics[ctx.guild] = []
            client = await channel.connect()
            message = await ctx.send(f"Je lance {video.url}")
            play_song(client, musics[ctx.guild], video)
            await message.add_reaction("▶")

    @client.command()
    async def join(ctx):
        channel = ctx.author.voice.channel
        await channel.connect()

   
   
    keep_alive()


    client.run(bottoken)
