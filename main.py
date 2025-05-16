import asyncio
import datetime
import os
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp

load_dotenv()

start_time = time.time()

# Use all intents, enabling presence explicitly is redundant since Intents.all() includes it
intents = discord.Intents.all()

description = "Yeetbot's owner commands"

client = commands.Bot(
    command_prefix='!',
    intents=intents,
    description=description,
    help_command=None  # We'll set PrettyHelp separately below
)

ending_note = f"For more info about a command and how to use it, use {client.command_prefix}help <command>."

# Set PrettyHelp with sorting, indexing, and categories
client.help_command = PrettyHelp(
    sort_commands=True,
    show_index=True,
    ending_note=ending_note,
    color=discord.Color.random(),
    no_category="Owner Commands",
    index_title="Yeetbot's commands"
)

color = discord.Color.dark_gold()


# Decorator to restrict commands to admins more cleanly
def admin_only():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)


@client.command(description='Load any cog extension.')
@admin_only()
async def load(ctx, extension):
    try:
        await client.load_extension(f'cogs.{extension}')
        await ctx.send(f'`{extension}` has been loaded.')
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f'`{extension}` is already loaded.')
    except commands.ExtensionNotFound:
        await ctx.send('`Invalid module.`')
    except commands.NoEntryPointError:
        await ctx.send('`The module has no setup function.`')
    except Exception as e:
        await ctx.send(f'Error loading module: `{e}`')


@client.command(description='Unload any cog extension.')
@admin_only()
async def unload(ctx, extension):
    try:
        await client.unload_extension(f'cogs.{extension}')
        await ctx.send(f'`{extension}` has been unloaded.')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'`{extension}` is not loaded.')
    except commands.ExtensionNotFound:
        await ctx.send('`Invalid module.`')
    except Exception as e:
        await ctx.send(f'Error unloading module: `{e}`')


@client.command(description='Reload a cog.')
@admin_only()
async def reload(ctx, extension):
    try:
        await client.reload_extension(f'cogs.{extension}')
        await ctx.send(f'`{extension}` has been reloaded.')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'`{extension}` is not loaded.')
    except commands.ExtensionNotFound:
        await ctx.send('`Invalid module.`')
    except Exception as e:
        await ctx.send(f'Error reloading module: `{e}`')


@client.event
async def on_ready():
    print(f'Bot ready. Logged in as {client.user}.')


async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'cogs.{filename[:-3]}')
            except Exception as e:
                print(f'Failed to load {filename}: {e}')


@client.command(description='Get how long the bot has been running.')
async def uptime(ctx):
    difference = int(time.time() - start_time)
    text = str(datetime.timedelta(seconds=difference))
    await ctx.send(f"`Current uptime: {text}`")


async def main():
    async with client:
        await load_extensions()
        await client.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
