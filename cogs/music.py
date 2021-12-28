from urllib.parse import urlparse
import discord
import asyncio
import random
from discord.ext.commands.converter import MemberConverter
import youtube_dl
import os
from youtubesearchpython import VideosSearch
from discord.ext import commands
import aiohttp
from discord import Spotify
import datetime as dt
import itertools
import functools
from enum import Enum
import asyncio
import logging

from async_timeout import timeout
from discord.ext import commands
import math

class AudioSourceType(Enum):
	SOURCE_UNKNOWN = 0
	SOURCE_YOUTUBE = 1
	SOURCE_YANDEXMUSIC = 2
	SOURCE_BANDCAMP = 3
	SOURCE_SOUNDCLOUD = 4
	SOURCE_SPOTIFY = 5
	
class AudioSourceIdentifier:
	@staticmethod
	def identify_source(search):

		YOUTUBE_DOMAIN_NAMES = ["www.youtube.com", "youtu.be"]
		YANDEXMUSIC_DOMAIN_NAMES = ["music.yandex.ru"]
		BANDCAMP_DOMAIN_NAMES = ["bandcamp.com"]
		SOUNDCLOUD_DOMAIN_NAMES = ["soundcloud.com"]
		SPOTIFY_DOMAIN_NAMES = ["spotify.com"]
		parsed_url = urlparse(search)

		if any(parsed_url.netloc in s for s in YOUTUBE_DOMAIN_NAMES):
			return AudioSourceType.SOURCE_YOUTUBE

		if any(parsed_url.netloc in s for s in YANDEXMUSIC_DOMAIN_NAMES):
			return AudioSourceType.SOURCE_YANDEXMUSIC

		if any(parsed_url.netloc in s for s in BANDCAMP_DOMAIN_NAMES):
			return AudioSourceType.SOURCE_BANDCAMP

		if any(parsed_url.netloc in s for s in SOUNDCLOUD_DOMAIN_NAMES):
			return AudioSourceType.SOURCE_SOUNDCLOUD

		if any(parsed_url.netloc in s for s in SPOTIFY_DOMAIN_NAMES):
			return AudioSourceType.SOURCE_SPOTIFY

		return AudioSourceType.SOURCE_UNKNOWN

class AudioSourceFactory:
	@staticmethod
	def provide_source(source_type):
		if source_type is AudioSourceType.SOURCE_YOUTUBE:
			return YTDLSource
		if source_type is AudioSourceType.SOURCE_UNKNOWN:
			return None

class SongQueue(asyncio.Queue):
	def __getitem__(self, item):
		if isinstance(item, slice):
			return list(itertools.islice(self._queue, item.start, item.stop, item.step))
		else:
			return self._queue[item]

	def __iter__(self):
		return self._queue.__iter__()

	def __len__(self):
		return self.qsize()

	def clear(self):
		self._queue.clear()

	def shuffle(self):
		random.shuffle(self._queue)

	def remove(self, index: int):
		del self._queue[index]

class VoiceError(Exception):
	pass

class YTDLError(Exception):
	pass

class PlayerError(Exception):
	pass

members = []

class YTDLSource(discord.PCMVolumeTransformer):
	YTDL_OPTIONS = {
		'format': 'bestaudio/best',
		'extractaudio': True,
		'audioformat': 'mp3',
		'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
		'restrictfilenames': True,
		'noplaylist': True,
		'nocheckcertificate': True,
		'ignoreerrors': False,
		'logtostderr': False,
		'quiet': True,
		'no_warnings': True,
		'default_search': 'auto',
		'source_address': '0.0.0.0',
	}

	FFMPEG_OPTIONS = {
		'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
		'options': '-vn',
	}

	ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

	def __init__(self, ctx, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
		super().__init__(source, volume)

		self.requester = ctx.author
		self.channel = ctx.channel
		self.data = data

		self.uploader = data.get('uploader')
		self.uploader_url = data.get('uploader_url')
		date = data.get('upload_date')
		self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
		self.title = data.get('title')
		self.thumbnail = data.get('thumbnail')
		self.description = data.get('description')
		self.duration = self.parse_duration(int(data.get('duration')))
		self.tags = data.get('tags')
		self.url = data.get('webpage_url')
		self.views = data.get('view_count')
		self.likes = data.get('like_count')
		self.dislikes = data.get('dislike_count')
		self.stream_url = data.get('url')

	def __str__(self):
		return '**{0.title}** by **{0.uploader}**'.format(self)

	@classmethod
	async def create_source(cls, ctx, search: str, *, loop: asyncio.BaseEventLoop = None):
		loop = loop or asyncio.get_event_loop()

		partial = functools.partial(
			cls.ytdl.extract_info, search, download=False, process=False)
		data = await loop.run_in_executor(None, partial)

		if data is None:
			raise YTDLError(
				'Couldn\'t find anything that matches `{}`'.format(search))

		if 'entries' not in data:
			process_info = data
		else:
			process_info = None
			for entry in data['entries']:
				if entry:
					process_info = entry
					break

			if process_info is None:
				raise YTDLError(
					'Couldn\'t find anything that matches `{}`'.format(search))

		webpage_url = process_info['webpage_url']
		partial = functools.partial(
			cls.ytdl.extract_info, webpage_url, download=False)
		processed_info = await loop.run_in_executor(None, partial)

		if processed_info is None:
			raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

		if 'entries' not in processed_info:
			info = processed_info
		else:
			info = None
			while info is None:
				try:
					info = processed_info['entries'].pop(0)
				except IndexError:
					raise YTDLError(
						'Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

		return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)


	@staticmethod
	def parse_duration(duration: int):
		minutes, seconds = divmod(duration, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)

		duration = []
		if days > 0:
			duration.append('{} days'.format(days))
		if hours > 0:
			duration.append('{} hours'.format(hours))
		if minutes > 0:
			duration.append('{} minutes'.format(minutes))
		if seconds > 0:
			duration.append('{} seconds'.format(seconds))

		return ', '.join(duration)

class Song:
	__slots__ = ('source', 'requester')

	def __init__(self, source: YTDLSource):
		self.source = source
		self.requester = source.requester

	def create_embed(self):
		embed = (discord.Embed(title='Now playing',
							   description='```css\n{0.source.title}\n```'.format(
								   self),
							   color=discord.Color.blurple())
				 .add_field(name='Duration', value=self.source.duration)
				 .set_footer(text=f'Requested by {self.requester.name}')
				 .add_field(name='Channel', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
				 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
				 .set_thumbnail(url=self.source.thumbnail))

		return embed

from youtube_dl.utils import YoutubeDLRedirectHandler

LYRICS_URL = "https://some-random-api.ml/lyrics?title="

class NoLyricsFound(commands.CommandError):
	pass

ytdl_format_options = {
	'audioquality': 5,
	'format': 'bestaudio',
	'outtmpl': '{}',
	'restrictfilenames': True,
	'flatplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': True,
	'logtostderr': False,
	"extractaudio": True,
	"audioformat": "opus",
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	# bind to ipv4 since ipv6 addresses cause issues sometimes
	'source_address': '0.0.0.0'}

ytdl_download_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': 'downloads/%(title)s.mp3',
	'reactrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': False,
	'default_search': 'auto',
	# bind to ipv4 since ipv6 addreacses cause issues sometimes
	'source_addreacs': '0.0.0.0',
	'output': r'youtube-dl',
	'postprocessors': [{
		'key': 'FFmpegExtractAudio',
		'preferredcodec': 'mp3',
		'preferredquality': '320',
	}]}

stim = {
	'default_search': 'auto',
	"ignoreerrors": True,
	'quiet': True,
	"no_warnings": True,
	"simulate": True,  # do not keep the video files
	"nooverwrites": True,
	"keepvideo": False,
	"noplaylist": True,
	"skip_download": False,
	# bind to ipv4 since ipv6 addresses cause issues sometimes
	'source_address': '0.0.0.0'}

ffmpeg_options = {
	'options': '-vn',
	# 'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
	}

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	# bind to ipv4 since ipv6 addresses cause issues sometimes
	'source_address': '0.0.0.0'}

ffmpeg_options = {
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

HUMANIZED_ACTIVITY = {
	discord.ActivityType.unknown: "Unknown activity",
	discord.ActivityType.playing: "Playing",
	discord.ActivityType.streaming: "Live on Twitch",
	discord.ActivityType.listening: "Listening",
	discord.ActivityType.watching: "Watching",
	discord.ActivityType.custom: "Custom status"}

def humanize_activity(activity_type: discord.ActivityType):
	return HUMANIZED_ACTIVITY.get(activity_type)

class VoiceStateManager:
	def __init__(self, bot: commands.Bot, ctx):
		self.bot = bot
		self._ctx = ctx

		self.current = None
		self.voice = None
		self.next = asyncio.Event()
		self.songs = SongQueue()

		self._loop = False
		self._volume = 0.5
		self.skip_votes = set()

		self.audio_player = bot.loop.create_task(self.audio_player_task())

	def __del__(self):
		self.audio_player.cancel()

	@property
	def loop(self):
		return self._loop

	@loop.setter
	def loop(self, value: bool):
		self._loop = value

	@property
	def volume(self):
		return self._volume

	@volume.setter
	def volume(self, value: float):
		self._volume = value

	@property
	def is_playing(self):
		return self.voice and self.current

	async def audio_player_task(self):
		while True:
			self.next.clear()

			if not self.loop:
				# Try to get the next song within 3 minutes.
				# If no song will be added to the queue in time,
				# the player will disconnect due to performance
				# reasons.
				try:
					async with timeout(180):  # 3 minutes
						self.current = await self.songs.get()
				except asyncio.TimeoutError:
					self.bot.loop.create_task(self.stop())
					return

			self.current.source.volume = self._volume
			self.voice.play(self.current.source, after=self.play_next_song)
			await self.current.source.channel.send(embed=self.current.create_embed())

			await self.next.wait()

	def play_next_song(self, error=None):
		if error:
			raise VoiceError(str(error))

		self.next.set()

	def skip(self):
		self.skip_votes.clear()

		if self.is_playing:
			self.voice.stop()

	async def stop(self):
		self.songs.clear()

		if self.voice:
			await self.voice.disconnect()
			self.voice = None
			try:
				del self.bot.get_cog(
					"MusicCogs").voice_states[self._ctx.guild.id]
			except KeyError:
				logging.info(
					"Guild ID has been removed from bot's pool already.")

class MusicPlayer(commands.Cog, name='Music'):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.voice_states = {}

	def get_voice_state(self, ctx):
		state = self.voice_states.get(ctx.guild.id)
		if not state:
			state = VoiceStateManager(self.bot, ctx)
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
		ctx.voice_state = self.get_voice_state(ctx)

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
		"""
		voice_state = ctx.author.voice

		if voice_state is None:
			# Exiting if the user is not in a voice channel
			return await ctx.send('`You need to be in a voice channel to use this command`')

		if not ctx.voice_state.is_playing:
			return await ctx.send('`I am not playing anything right now.`')

		voter = ctx.message.author
		if voter == ctx.voice_state.current.requester:
			await ctx.message.add_reaction('⏭')
			ctx.voice_state.skip()

		elif voter.id not in ctx.voice_state.skip_votes:
			ctx.voice_state.skip_votes.add(voter.id)
			total_votes = len(ctx.voice_state.skip_votes)

			percentagereq = 75
			percentage = (total_votes/len(members))*100

			if percentage >= 60:
				await ctx.message.add_reaction('⏭')
				ctx.voice_state.skip()
			else:
				await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))

		else:
			await ctx.send('`You have already voted to skip this song.`')

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
				audio_source_type = AudioSourceIdentifier.identify_source(search)
				audio_source = AudioSourceFactory.provide_source(audio_source_type)
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
	async def lyrics_command(self, ctx, *, name: str):
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

	@commands.command()
	async def musicsearch(self, ctx, query):
		videosSearch = VideosSearch(query, limit = 10)

		for i in range(len(videosSearch)):
			vid = videosSearch.resultComponents[i]
			await ctx.send(vid['title'])


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
				audio_source_type = AudioSourceIdentifier.identify_source(search)
				audio_source = AudioSourceFactory.provide_source(audio_source_type)
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

def setup(bot):
	bot.add_cog(MusicPlayer(bot))
