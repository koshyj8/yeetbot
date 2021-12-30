from urllib.parse import urlparse
import discord
import asyncio
import random
from discord.ext.commands.converter import MemberConverter
import youtube_dl
import os
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

from core.utils.music_utils import *


class TypeAudioSource(Enum):
	SOURCE_UNKNOWN = 0
	SOURCE_YOUTUBE = 1
	SOURCE_YANDEXMUSIC = 2
	SOURCE_BANDCAMP = 3
	SOURCE_SOUNDCLOUD = 4
	SOURCE_SPOTIFY = 5


class IdentifyAudioSource:
	@staticmethod
	def identify_source(search):

		YOUTUBE_DOMAIN_NAMES = ["www.youtube.com", "youtu.be"]
		YANDEXMUSIC_DOMAIN_NAMES = ["music.yandex.ru"]
		BANDCAMP_DOMAIN_NAMES = ["bandcamp.com"]
		SOUNDCLOUD_DOMAIN_NAMES = ["soundcloud.com"]
		SPOTIFY_DOMAIN_NAMES = ["spotify.com"]
		parsed_url = urlparse(search)

		if any(parsed_url.netloc in s for s in YOUTUBE_DOMAIN_NAMES):
			return TypeAudioSource.SOURCE_YOUTUBE

		if any(parsed_url.netloc in s for s in YANDEXMUSIC_DOMAIN_NAMES):
			return TypeAudioSource.SOURCE_YANDEXMUSIC

		if any(parsed_url.netloc in s for s in BANDCAMP_DOMAIN_NAMES):
			return TypeAudioSource.SOURCE_BANDCAMP

		if any(parsed_url.netloc in s for s in SOUNDCLOUD_DOMAIN_NAMES):
			return TypeAudioSource.SOURCE_SOUNDCLOUD

		if any(parsed_url.netloc in s for s in SPOTIFY_DOMAIN_NAMES):
			return TypeAudioSource.SOURCE_SPOTIFY

		return TypeAudioSource.SOURCE_UNKNOWN


class AudioFactory:
	@staticmethod
	def provide_source(source_type):
		if source_type is TypeAudioSource.SOURCE_YOUTUBE:
			return YTDLSource
		if source_type is TypeAudioSource.SOURCE_UNKNOWN:
			return None


class PlayerQueue(asyncio.Queue):
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


class VoiceStateController:
	def __init__(self, bot: commands.Bot, ctx):
		self.bot = bot
		self._ctx = ctx

		self.current = None
		self.voice = None
		self.next = asyncio.Event()
		self.songs = PlayerQueue()

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
