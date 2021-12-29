import discord
from discord import *
from discord.ext import commands
from discord.ext.commands.converter import MemberConverter
from discord_components import *

from discord.user import *
import urllib.parse, urllib.request
from math import floor
import psutil


HUMANIZED_ACTIVITY = {
	discord.ActivityType.unknown: "Unknown activity",
	discord.ActivityType.playing: "Playing",
	discord.ActivityType.streaming: "Live on Twitch",
	discord.ActivityType.listening: "Listening",
	discord.ActivityType.watching: "Watching",
	discord.ActivityType.custom: "Custom status"}

def humanize_activity(activity_type: discord.ActivityType):
	return HUMANIZED_ACTIVITY.get(activity_type)

googleapi = 'AIzaSyDTt8PuXgGn8YtJMk6-F7YtpRthclZbF00'
API_KEY = '336d22fbad9d8795237e2abee2d4c32a'

class Information(commands.Cog):
	'''Commands for information'''
	def __init__(self,bot):
		self.bot = bot

	@commands.command(aliases=['uinfo', 'minfo', 'ui'], brief='Get information about a user\'s account')
	async def userinfo(self, ctx, member:MemberConverter = None):
		'''Get the user's information'''

		if member == None:
			member=ctx.message.author

		if member.bot==True:

			roles = [role for role in member.roles[1:]]
			embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

			for activity in member.activities:
				if isinstance(activity, discord.Spotify):
					track_url = f"https://open.spotify.com/track/{activity.track_id}"
					artists = ", ".join(activity.artists)
					value = f"[{artists} — {activity.title}]({track_url})"

					embed.add_field(
						name="Listening", value=value, inline=False)

				else:
					embed.add_field(name=humanize_activity(
						activity.type), value=f"{activity.name}", inline=False)


			embed.set_author(name=f"{member}'s Information")
			embed.set_thumbnail(url=member.avatar_url)

			embed.add_field(name="Member ID:", value=member.id)
			embed.add_field(name="Nickname:", value=member.display_name)

			embed.add_field(name="Created At:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
			embed.add_field(name="Joined:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
			embed.add_field(name=f"Roles: ({len(roles)})", value=" ".join([role.mention for role in roles]))
			embed.add_field(name="Top Role:", value=member.top_role.mention)

			embed.add_field(name="Is the member a bot?", value=member.bot)

			await ctx.send(embed=embed)

		else:
			roles = [role for role in member.roles[1:]]
			embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

			for activity in member.activities:
				if isinstance(activity, discord.Spotify):
					track_url = f"https://open.spotify.com/track/{activity.track_id}"
					artists = ", ".join(activity.artists)
					value = f"[{artists} — {activity.title}]({track_url})"

					embed.add_field(
						name="Listening", value=value, inline=False)

				else:
					embed.add_field(name=humanize_activity(
						activity.type), value=f"{activity.name}", inline=False)


			embed.set_author(name=f"{member}'s Information")

			embed.add_field(name="Member ID:", value=member.id)
			embed.add_field(name="Nickname:", value=member.display_name)

			embed.add_field(name="Created At:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
			embed.add_field(name="Joined:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
			embed.add_field(name=f"Roles: ({len(roles)})", value=" ".join([role.mention for role in roles]))
			embed.add_field(name="Top Role:", value=member.top_role.mention)

			embed.add_field(name="Is the member a bot?", value=member.bot)

			await ctx.send(embed=embed)

			if member.id == 680773275948679195:
				await ctx.send("`just kidding he is a bot!`")

	@commands.command()
	async def invite(self,ctx):
		'''Bot Invite Link'''
		await ctx.send("`Bot Invite Link`",components=[Button(style=ButtonStyle.URL, label="Invite", url="https://discord.com/oauth2/authorize?client_id=760126094338031626&permissions=8&scope=bot")])
		
	@commands.command()
	async def serverinvite(self, ctx):
		'''A one time server invite'''
		invitelink = await ctx.channel.create_invite(max_age = 90, max_uses=1, unique=True)
		res = str(invitelink)
		await ctx.send("`Server Invite Link`", components=[Button(style=ButtonStyle.URL, label="Invite", url=res)])

	@commands.command(aliases=['latency'])
	async def ping(self, ctx):
		'''Send bot latency'''
		await ctx.send("`Ping: {0:.2f}ms`".format(round(self.bot.latency*1000, 1)))

	@commands.command()
	async def emojis(self, ctx):
		'''Lists all emojis in a server'''
		emotes = '\n'.join(['{1} `:{0}:`'.format(e.name, str(e)) for e in ctx.message.guild.emojis])
		if len(emotes) > 2000:
			paginated_text = ctx.paginate(emotes)
			for page in paginated_text:
				if page == paginated_text[-1]:
					await ctx.send(f'{page}')
					break
				await ctx.send(f'{page}')

		else:
			await ctx.send(emotes)

	@commands.command()
	async def cmds(self,ctx):
		res = len(self.bot.commands)
		await ctx.send(f"`This bot has {res} commands.`")

	@commands.command()
	async def presence(self,ctx,member:MemberConverter=None):
		member = member or ctx.author
		activity = discord.utils.find(lambda a: isinstance(a, discord.Status), member.activities)
		embed=discord.Embed(title=f'{member}\'s status',color=discord.Color.random())
		for activity in member.activities:
			if activity == False:
				await ctx.send(f"`{member} is not doing anything right now.`")
				break

			elif isinstance(activity, discord.Spotify):
				track_url = f"https://open.spotify.com/track/{activity.track_id}"
				artists = ", ".join(activity.artists)
				value = f"[{artists} — {activity.title}]({track_url})"
				embed.add_field(
					name="Listening", value=value, inline=False)
			else:
				embed.add_field(name=humanize_activity(
					activity.type), value=f"{activity.name}", inline=False)
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Information(bot))
