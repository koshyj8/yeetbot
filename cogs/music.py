from urllib.parse import urlparse
import discord
import asyncio
from discord.ext.commands.converter import MemberConverter
import youtube_dl
import os
from discord.ext import commands
import aiohttp
from discord import Spotify
import datetime as dt
from enum import Enum
import asyncio
import logging

from async_timeout import timeout
from discord.ext import commands
import math

loop = False

from core.utils.music_utils import *

HUMANIZED_ACTIVITY = {
	discord.ActivityType.unknown: "Unknown activity",
	discord.ActivityType.playing: "Playing",
	discord.ActivityType.streaming: "Live on Twitch",
	discord.ActivityType.listening: "Listening",
	discord.ActivityType.watching: "Watching",
	discord.ActivityType.custom: "Custom status"}

def humanize_activity(activity_type: discord.ActivityType):
	return HUMANIZED_ACTIVITY.get(activity_type)

class MusicPlayer(commands.Cog, name='Music'):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.voice_states = {}

	def get_user_voice_state(self, ctx):
		state = self.voice_states.get(ctx.guild.id)
		if not state or not state.exists:
			state = VoiceStateController(self.bot, ctx)
			self.voice_states[ctx.guild.id] = state

		return state

	def cog_unload(self):
		for state in self.voice_states.values():
			self.bot.loop.create_task(state.stop())

	def cog_check(self, ctx):
		if not ctx.guild:
			raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

		return True

	async def cog_before_invoke(self, ctx):
		ctx.voice_state = self.get_user_voice_state(ctx)

	@commands.command(name='musicsearch')
	async def _search(self, ctx: commands.Context, *, search: str):
		"""Searches youtube.
		It returns an imbed of the first 10 results collected from youtube.
		Then the user can choose one of the titles by typing a number
		in chat or they can cancel by typing "cancel" in chat.
		Each title in the list can be clicked as a link.
		"""
		async with ctx.typing():
			try:
				source = await YTDLSource.search_source(ctx, search, loop=self.bot.loop, bot=self.bot)
			except YTDLError as e:
				await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
			else:
				if source == 'sel_invalid':
					await ctx.send('Invalid selection')
				elif source == 'cancel':
					await ctx.send(':white_check_mark:')
				elif source == 'timeout':
					await ctx.send(':alarm_clock: **Time\'s up bud**')
				else:
					if not ctx.voice_state.voice:
						await ctx.invoke(self._join)

					song = Song(source)
					await ctx.voice_state.songs.put(song)
					await ctx.send('Enqueued {}'.format(str(source)))

	@commands.command(name='join', invoke_without_subcommand=True)
	async def _join(self, ctx):
		"""Joins a voice channel."""

		destination = ctx.author.voice.channel
		if ctx.voice_state.voice:
			await ctx.voice_state.voice.move_to(destination)
			return

		ctx.voice_state.voice = await destination.connect()
		await ctx.send("`Bot has joined voice channel.`")

	@commands.command(name='summon')
	async def _summon(self, ctx, *, channel: discord.VoiceChannel = None):
		"""Summons the bot to a voice channel.
		If no channel was specified, it joins your channel.
		"""

		if not channel and not ctx.author.voice:
			raise VoiceError('`Please join a voice channel or specify a channel to join.`')

		destination = channel or ctx.author.voice.channel
		if ctx.voice_state.voice:
			await ctx.voice_state.voice.move_to(destination)
			return

		ctx.voice_state.voice = await destination.connect()

	@commands.command(name='leave', aliases=['disconnect'])	
	async def _leave(self, ctx):
		"""Clears the queue and leaves the voice channel."""
		voice_state = ctx.author.voice

		if voice_state is None:
			# Exiting if the user is not in a voice channel
			return await ctx.send('`You need to be in a voice channel to use this command`')

		try:
			if not ctx.voice_state.voice:
				return await ctx.send('`Not connected to any voice channel.`')
			await ctx.voice_state.stop()
			del self.voice_states[ctx.guild.id]
		except Exception:
			print('Exception during exit: {0}'.format(Exception))

	@commands.command(name='now', aliases=['current', 'playing'])
	async def _now(self, ctx):
		"""Displays the currently playing song."""

		await ctx.send(embed=ctx.voice_state.current.create_embed())

	@commands.command(name='pause')
	async def _pause(self, ctx):
		"""Pauses the currently playing song."""
		voice_state = ctx.author.voice

		if voice_state is None:
			# Exiting if the user is not in a voice channel
			return await ctx.send('`You need to be in a voice channel to use this command`')
		voice_state = ctx.author.voice

		if voice_state is None:
			# Exiting if the user is not in a voice channel
			return await ctx.send('`You need to be in a voice channel to use this command`')
		if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
			ctx.voice_state.voice.pause()
			await ctx.send("`Song has been paused.`")

	@commands.command(name='resume', aliases=['res'])	
	async def _resume(self, ctx):
		"""Resumes a currently paused song."""
		voice_state = ctx.author.voice

		if voice_state is None:
			# Exiting if the user is not in a voice channel
			return await ctx.send('`You need to be in a voice channel to use this command`')
		if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
			ctx.voice_state.voice.resume()
			await ctx.send("`Song has been resumed.`")

	@commands.command(name='stop')
	async def _stop(self, ctx):
		"""Stops playing song and clears the queue."""
		voice_state = ctx.author.voice

		if voice_state is None:
			# Exiting if the user is not in a voice channel
			return await ctx.send('`You need to be in a voice channel to use this command`')
		ctx.voice_state.songs.clear()

		if ctx.voice_state.is_playing:
			ctx.voice_state.voice.stop()
			await ctx.send("`Song has been stopped, and queue has been cleared.`")

	@commands.command(name='skip')
	@commands.has_role("DJ")
	async def _skip(self, ctx):
		"""Vote to skip a song. The requester can automatically skip.
		3 skip votes are needed for the song to be skipped.
		"""
		members = len(ctx.author.voice.channel.voice_states.keys())
		if not ctx.voice_state.is_playing:
			return await ctx.send('Not playing any music right now...')

		voter = ctx.message.author
		if voter == ctx.voice_state.current.requester:		
			ctx.voice_state.skip()
			await ctx.message.add_reaction('⏭')

		elif voter.id not in ctx.voice_state.skip_votes:
			ctx.voice_state.skip_votes.add(voter.id)
			total_votes = len(ctx.voice_state.skip_votes)

			if total_votes > 1/2 * members:
				ctx.voice_state.skip()
				await ctx.message.add_reaction('⏭')
			else:
				await ctx.send(f'Skip vote added, currently at **{total_votes}/{members-1}**')

		else:
			await ctx.send('You have already voted to skip this song.')

	@commands.command(name='queue',aliases=['q'])
	async def _queue(self, ctx, *, page: int = 1):
		"""Shows the player's queue.
		"""

		if len(ctx.voice_state.songs) == 0:
			return await ctx.send('Empty queue.')

		items_per_page = 10
		pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

		start = (page - 1) * items_per_page
		end = start + items_per_page

		queue = ''
		for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
			queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

		embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
				 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
		await ctx.send(embed=embed)

	@commands.command(name='loop')
	async def _loop(self, ctx: commands.Context):
		"""Loops the currently playing song.
		Invoke this command again to unloop the song.
		"""

		if not ctx.voice_state.is_playing:
			return await ctx.send('Nothing being played at the moment.')

		# Inverse boolean value to loop and unloop.
		ctx.voice_state.loop = not ctx.voice_state.loop
		await ctx.message.add_reaction('✅')

	@commands.command(name='shuffle', aliases=['shuff'])
	@commands.has_role("DJ")
	async def _shuffle(self, ctx):
		"""Shuffles the queue."""

		if len(ctx.voice_state.songs) == 0:
			return await ctx.send('Empty queue.')

		ctx.voice_state.songs.shuffle()
		await ctx.send("`Queue has been successfully shuffled.`")

	@commands.command(name='remove')
	@commands.has_role("DJ")
	async def _remove(self, ctx, index: int):
		"""Removes a song from the queue at a given index."""

		if len(ctx.voice_state.songs) == 0:
			return await ctx.send('`Empty queue.`')

		ctx.voice_state.songs.remove(index - 1)
		await ctx.send(f"`Song Number {index} has been removed.`")

	@commands.command(name='play')
	async def _play(self, ctx, *, search: str):
		"""Plays a song.
		"""

		if search.startswith('https://open.spotify.com/'):
			return

		if not ctx.voice_state.voice:
			await ctx.invoke(self._join)

		async with ctx.typing():
			try:
				audio_source_type = IdentifyAudioSource.identify_source(search)
				audio_source = AudioFactory.provide_source(audio_source_type)
				if audio_source is not None:
					# TODO ?
					source = await audio_source.create_source(ctx, search, loop=self.bot.loop)
				else:
					await ctx.send('`{} is not supported source.`'.format(str(search)))
			except PlayerError as e:
				await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
			else:
				song = Song(source)

				await ctx.voice_state.songs.put(song)

				await ctx.send('Enqueued {}'.format(str(source)))

	@_join.before_invoke
	@_play.before_invoke
	async def ensure_voice_state(self, ctx):
		if not ctx.author.voice or not ctx.author.voice.channel:
			raise commands.CommandError('`You are not connected to any voice channel.`')

		if ctx.voice_client:
			if ctx.voice_client.channel != ctx.author.voice.channel:
				raise commands.CommandError('`Bot is already in a voice channel.`')

	@commands.command(brief='Download songs', aliases=['find','dl'])
	@commands.cooldown(1, 120, commands.BucketType.user)
	async def download(self, ctx, *, song):
		'''download a song'''
		await ctx.send(f"`This will take some time as it downloads on S C A R R E D's device.`")
		try:
			with youtube_dl.YoutubeDL(ytdl_download_format_options) as ydl:
				if "https://www.youtube.com/" in song:
					download = ydl.extract_info(song, True)
				else:
					infosearched = ydl.extract_info(
						"ytsearch:"+song, False)
					download = ydl.extract_info(
						infosearched['entries'][0]['webpage_url'], True)
				filename = ydl.prepare_filename(download)
				b = os.path.getsize(filename)
				if b > 10000000:
					await ctx.send('`That download is greater than 100MB, i wont send it, bitch`')
				else:
					time = await ctx.send("`The download will be uploaded shortly.`")
					await asyncio.sleep(10)
					await time.delete()
					await ctx.send(file=discord.File(filename))
					os.remove(filename)
		except (youtube_dl.utils.ExtractorError, youtube_dl.utils.DownloadError):
			embed = discord.Embed(
				title="Song couldn't be downloaded", description=("Song:"+song))
			await ctx.send(embed=embed)

	@commands.command(name="lyrics")
	async def lyrics_command(self, ctx, *, name: str = None):
		name = name or Song.create_embed.title
		async with aiohttp.request("GET", LYRICS_URL + name, headers={}) as r:
			if not 200 <= r.status <= 299:
				raise NoLyricsFound

			data = await r.json()

			if len(data["lyrics"]) > 2000:
				return await ctx.send(f"`(There were over 2000 characters)`<{data['links']['genius']}>")

			embed = discord.Embed(
				title=data["title"],
				description=data["lyrics"],
				colour=ctx.author.colour,
				timestamp=dt.datetime.utcnow(),
			)
			embed.set_thumbnail(url=data["thumbnail"]["genius"])
			embed.set_author(name=data["author"])
			await ctx.send(embed=embed)

	@lyrics_command.error
	async def lyrics_command_error(self, ctx, exc):
		if isinstance(exc, NoLyricsFound):
			await ctx.send("No lyrics could be found.")

	@commands.command(aliases=['spotdownload','spotdl'])
	@commands.cooldown(1, 120, commands.BucketType.user)
	async def spotifydownload(self, ctx, user: MemberConverter = None):
		'''Downloads the song a user is listening to on spotify.'''
		if user == None:
			user = ctx.author

		if user.activities:
			for activity in user.activities:
				if isinstance(activity, Spotify):
					activitymusicname = activity.title

		with youtube_dl.YoutubeDL(ytdl_download_format_options) as ydl:
			infosearched = ydl.extract_info("ytsearch:"+activitymusicname, False)
			download = ydl.extract_info(
				infosearched['entries'][0]['webpage_url'], True)
			filename = ydl.prepare_filename(download)
			time = await ctx.send('`File will be uploaded shortly.`')
			b = os.path.getsize(filename)
			if b > 1000000:
				await ctx.send('`That download is greater than 100MB, i wont send it, bitch`')
			else:
				await asyncio.sleep(10)
				await time.delete()
				await ctx.send(file=discord.File(filename))
				os.remove(filename)

	@commands.command()
	async def spotify(self, ctx, member: MemberConverter = None):
		'''Get the link of the song someone is listening too.'''
		member = member or ctx.author
		activity = discord.utils.find(lambda a: isinstance(
			a, discord.Spotify), member.activities)

		if not activity:
			return await ctx.send(f"`{member} is not listening to Spotify right now.`")

		track_url = f"https://open.spotify.com/track/{activity.track_id}"
		await ctx.send(track_url)

	@commands.Cog.listener()
	async def on_voice_state_update(member, before, after):
		if not before.channel and after.channel:
			members.append(member.id)
		elif before.channel and not after.channel:
			members.remove(member.id)

	@commands.command()
	async def playsp(self, ctx, user: MemberConverter = None):
		'''Information about someone's spotify status.'''
		if user == None:
			user = ctx.author
			pass
		if user.activities:
			for activity in user.activities:
				if isinstance(activity, Spotify):
					search = activity.title

		async with ctx.typing():
			try:
				audio_source_type = IdentifyAudioSource.identify_source(search)
				audio_source = AudioFactory.provide_source(audio_source_type)
				if audio_source is not None:
					# TODO ?
					source = await audio_source.create_source(ctx, search, loop=self.bot.loop)
				else:
					await ctx.send('`{} is not supported source.`'.format(str(search)))
			except PlayerError as e:
				await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
			else:
				song = Song(source)

				await ctx.voice_state.songs.put(song)

				await ctx.send('Enqueued {}'.format(str(source)))

	@_join.before_invoke
	@_play.before_invoke
	@_remove.before_invoke
	@_shuffle.before_invoke
	@_loop.before_invoke
	@_queue.before_invoke
	@_skip.before_invoke
	@_pause.before_invoke
	@_resume.before_invoke
	@_leave.before_invoke
	async def ensure_voice_state(self, ctx: commands.Context):
		if not ctx.author.voice or not ctx.author.voice.channel:
			raise commands.CommandError('`You are not connected to any voice channel.`')

		if ctx.voice_client:
			if ctx.voice_client.channel != ctx.author.voice.channel:
				raise commands.CommandError('`Bot is already in a voice channel.`')

def setup(bot):
	bot.add_cog(MusicPlayer(bot))
