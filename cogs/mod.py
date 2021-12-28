import asyncio
import discord
import re
from discord import utils
from discord import colour
from discord.ext import commands
from discord.ext.commands.converter import MemberConverter

ALPHABET = {'a': '🇦', 'b': '🇧', 'c': '🇨', 'd': '🇩', 'e': '🇪', 'f': '🇫', 'g': '🇬', 'h': '🇭', 'i': '🇮',
			'j': '🇯',
			'k': '🇰', 'l': '🇱', 'm': '🇲', 'n': '🇳', 'o': '🇴', 'p': '🇵', 'q': '🇶', 'r': '🇷', 's': '🇸',
			't': '🇹',
			'u': '🇺', 'v': '🇻', 'w': '🇼', 'x': '🇽', 'y': '🇾', 'z': '🇿'}  # letter: emoji

COLORS = {"blue": "🟦", "green": "🟩", "red": "🟥",
		  "yellow": "🟨", "white": "⬜", "purple": "🟪", "orange": "🟧"}

NUMBERS = {0: "0️⃣", 1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣",
		   5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣"}

from discord.member import Member

def getGuild(ctx, msg):
	if msg == '':
		return ctx.guild
	elif msg.isdigit():
		return ctx.bot.get_guild(int(msg))
	else:
		return utils.find(lambda g: msg.lower() in g.name.lower(), ctx.bot.guilds)
	return None

def getChannel(ctx, msg):
	if msg == '':
		return ctx.channel
	elif 1 == len(ctx.message.channel_mentions):
		return ctx.message.channel_mentions[0]
	elif msg.isdigit():
		return ctx.bot.get_channel(int(msg))
	elif utils.find(lambda c: msg.lower() in c.name.lower(), ctx.guild.text_channels):
		return utils.find(lambda c: msg.lower() in c.name.lower(), ctx.guild.text_channels)
	else:
		return utils.find(lambda c: msg.lower() in c.name.lower(), ctx.bot.get_all_channels())
	return None

def getRole(ctx, msg):
	if msg == '':
		return ctx.guild.default_role
	if 1 == len(ctx.message.role_mentions):
		return ctx.message.role_mentions[0]
	elif msg.isdigit():
		return utils.find(lambda r: msg.strip() == r.id, ctx.guild.roles)
	else:
		return utils.find(lambda r: msg.strip().lower() in r.name.lower(), ctx.guild.roles)
	return None

def getEmote(ctx, content):
	emoji_reg = re.compile(r'<:.+?:([0-9]{15,21})>').findall(content)
	if emoji_reg:
		return ctx.bot.get_emoji(int(emoji_reg[0]))
	elif content.strip().isdigit():
		return ctx.bot.get_emoji(int(content.strip()))
	return None

class Moderation(commands.Cog):
	'''The admin commands for a discord server'''
	def __init__(self, bot):
		self.bot = bot

	async def do_purge(self, ctx, limit, predicate):
		if limit:
			deleted = await ctx.channel.purge(limit=limit, before=ctx.message, check=predicate)
			message=await ctx.send(f"`Deleted {limit} messages`")
			await ctx.message.delete()
			await asyncio.sleep(5)
			await message.delete()

		else:
			await ctx.edit(content="How many messages do you want to delete?", ttl=5)

	@commands.group()
	@commands.guild_only()
	async def purge(self, ctx):
		"""Remove certain messages."""
		if ctx.invoked_subcommand is None:
			pass

	@purge.command()
	@commands.has_permissions(manage_messages=True)
	async def embeds(self, ctx, search: int = None):
		"""Remove embed messages."""
		await self.do_purge(ctx, search, lambda e: len(e.embeds));

	@purge.command()
	@commands.has_permissions(manage_messages=True)
	async def attachments(self, ctx, search: int = None):
		"""Remove messages with attachments."""
		await self.do_purge(ctx, search, lambda e: len(e.attachments))

	@purge.command(name='all')
	@commands.has_permissions(manage_messages=True)
	async def _all(self, ctx, search: int = None):
		"""Remove all Messages."""
		await self.do_purge(ctx, search, lambda e: True)
	
	@purge.command()
	@commands.has_permissions(manage_messages=True)
	async def user(self, ctx, mem:discord.Member, search: int = None):
		"""Removes Messages of a certain User."""
		if mem.id == 275609153274380289:
			await ctx.send("Koshy has made himself invulnerable to this command.")
		else:
			await self.do_purge(ctx, search, lambda e: e.author == mem)

	@purge.command()
	async def me(self, ctx, search: int = None):
		"""Remove messages sent by me."""
		await self.do_purge(ctx, search, lambda e: e.author == ctx.author)

	@commands.group(brief='Lets an admin edit a channel',aliases=['ec','channeledit','ce'])
	@commands.has_permissions(manage_channels=True)
	async def editchannel(self,ctx):
		if ctx.invoked_subcommand is None:
			pass

	@editchannel.command(brief='Lets a user with permissions change the channel name.')
	@commands.has_permissions(manage_channels=True)
	async def name(self,ctx,*, name):
		await ctx.channel.edit(name=name)
		await ctx.send(f'Channel Name has been set to {name}.')

	@editchannel.command(brief='Toggle OFF/ON NSFW')
	async def nsfw(self,ctx,channel:discord.TextChannel=None):
		if ctx.channel_is_nsfw():
			await ctx.channel.edit(nsfw=False)
			await ctx.send(f"`Successfully toggled off NSFW`")
		else:
			await ctx.channel.edit(nsfw=True)
			await ctx.send(f"`Successfully toggled on NSFW`")

	@commands.command(brief='Create a text channel',aliases=['channelcrea','creachannel','chancrea','cc'])
	@commands.has_permissions(administrator=True)
	async def createch(self,ctx,*,name):
		guild = ctx.message.guild
		await guild.create_text_channel(name)
		await ctx.send(f'Successfully created #{name}')

	@commands.command(brief='Delete a text channel',aliases=['channeldel','delchan','chandel','cd'])
	@commands.has_permissions(administrator=True)
	async def deletech(self,ctx, channel:discord.TextChannel):
		guild = ctx.message.guild
		await channel.delete()
		await ctx.send(f'Successfully deleted **{channel}**')

	@commands.bot_has_permissions(manage_emojis=True)
	@commands.has_permissions(manage_emojis=True)
	@commands.command(aliases=['emoadd','addemoji','aemoji'])
	async def emojiadd(self, ctx, name: str):
		if not ctx.message.attachments:
			raise commands.BadArgument("`You have to upload image along with the command`")

		attachment = ctx.message.attachments[0]
		if attachment.size > 256000:
			return await ctx.send("`File size should be < 256 kilobytes`")

		b = await attachment.read()
		e = await ctx.guild.create_custom_emoji(name=name, image=b)

		await ctx.send(f"{e} has been uploaded")

	@commands.command(aliases=['sername','nameserver','ns','sn'])
	@commands.has_permissions(administrator=True)
	async def servername(self,ctx,*,name):
		'''Change a server name'''
		await ctx.guild.edit(name=name)
		await ctx.send(f"`Successfully changed server name.`")
	
	@commands.command()
	async def talk(self, ctx, message:str, author:MemberConverter=None):
		if author == None:
			author = ctx.author
		webhooks = await ctx.channel.webhooks()
		webhook = utils.get(webhooks, name="yeet")
		if webhook is None:
			webhook = await ctx.channel.create_webhook(name = "yeet")
		await webhook.send(message, username = author.display_name, avatar_url = author.avatar_url)
		await ctx.message.delete()

def setup(bot):
	bot.add_cog(Moderation(bot))
