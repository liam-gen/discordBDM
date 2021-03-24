import discord
import discord.ext
from discord.ext import commands
import DiscordUtils
import random
import os
import asyncio



def bot(prefix, description, token, status, color):
    botprefix = prefix
    botdescription = description
    bottoken = token
    botstatus = status
    botcolor = color
    client = commands.Bot(command_prefix=botprefix, description=botdescription)

    @client.event
    async def on_ready():
        print(
            f"Le bot {client.user.name} a été lancé ! \nStatistiques \nServeurs : {len(client.guilds)}\n\n----------\n\nChargement ...\nStatus : {botstatus}\nPréfix : {botprefix}\nDescription : {botdescription}\n\n----------"
        )
        await client.change_presence(activity=discord.Game(name=botstatus))

    @client.command()
    async def ping(ctx):
        latence = client.latency * 1000
        await ctx.send(f"Pong , je t'ai répondu en {round(latence)}ms !")

    @client.command()
    @command.has_permission(kick_members=True)
    async def kick(ctx, member: discord.Member):
        try:
            await member.kick(reason=f"Kick par {ctx.author.name} - {client.user.name} Mod")
            embed = discord.Embed(title="Une nouvelle expulsion !", description=f"Oust **{member.name}** ! Il a été expluser par **{ctx.author.name}**!", colour=botcolor)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Une erreur s'est produite")

    @client.remove_command("help")
    @client.command()
    async def help(ctx):
        embed1 = discord.Embed(title="Page d'aide 0/2",
                              description="Sommaire :\n\nPage 1 : Bot\nPage 2 : Modération",
                              colour=botcolor)
        embed2 = discord.Embed(title="Page d'aide 1/2 - Bot", description=f"**Commandes**\n\n`{botprefix}ping`", colour=botcolor)
        embed3 = discord.Embed(title="Page 2/2 - Modération", description=f"**Commandes**\n\n`{botprefix}kick`", colour=botcolor)
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
        paginator.add_reaction("⬅", "back")
        paginator.add_reaction("🔲", "lock")
        paginator.add_reaction("➡", "next")
        embeds = [embed1, embed2, embed3]
        await paginator.run(embeds)

    client.run(bottoken)
