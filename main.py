import asyncio
import datetime
import json
import os
import random
import time
from random import choice

import discord
from discord import *
from discord.ext import commands
from discord.ext.commands.converter import MemberConverter
from dotenv import load_dotenv
from pretty_help import PrettyHelp

load_dotenv()

start_time = time.time()

intents = discord.Intents.all()
intents.presences = True
description = '''Yeetbot's owner commands'''
client = commands.Bot(command_prefix='!', intents=intents,
                      help_command=PrettyHelp(), description=description)
ending_note = f"For more info about a command and how to use it, use {client.command_prefix}help <command> ."


client.help_command = PrettyHelp(sort_commands=True, show_index=True, ending_note=ending_note,
                                 color=discord.Color.random(), no_category="Owner Commands", index_title=f"Yeetbot's commands")

color = discord.Color.dark_gold()


@client.command(description='Load any cog extension.')
async def load(ctx, extension):
	if not ctx.author.guild_permissions.administrator:
		return
	try:
		await client.load_extension(f'cogs.{extension}')
		await ctx.send(f'`{extension}` `has been loaded.`')
	except:
		await ctx.send("`Invalid module.`")

@client.command(description='Unload any cog extension.')
async def unload(ctx, extension):
	if not ctx.author.guild_permissions.administrator:
		return
	try:
		await client.unload_extension(f'cogs.{extension}')
		await ctx.send(f'`{extension}` `has been unloaded.`')
	except:
		await ctx.send("`Invalid module.`")


@client.command(description='Reload a cog.')
async def reload(ctx, extension):
	if not ctx.author.guild_permissions.administrator:
		return
	try:
		await client.reload_extension(f'cogs.{extension}')
		await ctx.send(f'`{extension}` `has been reloaded.`')
	except:
		await ctx.send("`Invalid module.`")



@client.event
async def on_ready():
	print('Bot ready.')



async def load_extensions():
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			await client.load_extension(f'cogs.{filename[:-3]}')


@client.command(description='Get how long the bot has been running.')
async def uptime(ctx):
	current_time = time.time()
	difference = int(round(current_time - start_time))
	text = str(datetime.timedelta(seconds=difference))
	await ctx.send(f"`Current uptime: {text}`")


async def main():
    async with client:
        await load_extensions()
        await client.start(os.getenv("discord_TOKEN"))

asyncio.run(main())
