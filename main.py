from discord.ext import commands
import os
from discord.ext.commands.converter import MemberConverter
from dotenv.main import DotEnv
import json
import asyncio
import datetime,time
from dotenv import load_dotenv
from boto.s3.connection import S3Connection
import asyncio
from pretty_help import PrettyHelp

import discord
from cogwatch import Watcher
from discord import *
import random
from random import choice
from discord.ext import commands
load_dotenv()

start_time = time.time()


intents = discord.Intents.all()
intents.presences = True
description = '''Yeetbot's owner commands'''
client = commands.Bot(command_prefix='!', intents=intents, help_command=PrettyHelp(), description=description)

ending_note = f"For more info about a command and how to use it, use {client.command_prefix}help <command> ."



client.help_command = PrettyHelp(sort_commands = True, show_index = True, ending_note=ending_note, color = discord.Color.random(), no_category = "Owner Commands", index_title = f"Yeetbot's commands")

color = discord.Color.dark_gold()


@client.command(brief='Load any cog extension.')
@commands.is_owner()
async def load(ctx, extension):
		client.load_extension(f'cogs.{extension}')
		await ctx.send(f'`{extension}` `has been loaded.`')

@client.command(brief='Unload any cog extension.')
@commands.is_owner()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	await ctx.send(f'`{extension}` `has been unloaded.`')

@client.command(brief='reload any cog extension.')
@commands.is_owner()
async def reload(ctx, extension):
	client.reload_extension(f'cogs.{extension}')
	await ctx.send(f'`{extension}` `has been reloaded.`')

@client.event
async def on_ready():
	print('Bot ready.')

	watcher = Watcher(client, path='cogs')
	await watcher.start()


@client.command()
async def uptime(ctx):
	current_time = time.time()
	difference = int(round(current_time - start_time))
	text = str(datetime.timedelta(seconds=difference))
	await ctx.send(f"`Current uptime: {text}`")

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')


client.run(os.getenv("discord_TOKEN"))
