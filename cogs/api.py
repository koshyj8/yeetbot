from datetime import datetime
from aiohttp.client import ClientSession
from discord.ext import commands
import discord
import datetime
import aiohttp
import requests
import praw
from praw import reddit
import randfacts
from collections import namedtuple
import re
import asyncio

langsi ={"entries": {
	'af': 'afrikaans',
	'sq': 'albanian',
	'am': 'amharic',
	'ar': 'arabic',
	'hy': 'armenian',
	'az': 'azerbaijani',
	'eu': 'basque',
	'be': 'belarusian',
	'bn': 'bengali',
	'bs': 'bosnian',
	'bg': 'bulgarian',
	'ca': 'catalan',
	'ceb': 'cebuano',
	'ny': 'chichewa',
	'zh-cn': 'chinese (simplified)',
	'zh-tw': 'chinese (traditional)',
	'co': 'corsican',
	'hr': 'croatian',
	'cs': 'czech',
	'da': 'danish',
	'nl': 'dutch',
	'en': 'english',
	'eo': 'esperanto',
	'et': 'estonian',
	'tl': 'filipino',
	'fi': 'finnish',
	'fr': 'french',
	'fy': 'frisian',
	'gl': 'galician',
	'ka': 'georgian',
	'de': 'german',
	'el': 'greek',
	'gu': 'gujarati',
	'ht': 'haitian creole',
	'ha': 'hausa',
	'haw': 'hawaiian',
	'iw': 'hebrew',
	'he': 'hebrew',
	'hi': 'hindi',
	'hmn': 'hmong',
	'hu': 'hungarian',
	'is': 'icelandic',
	'ig': 'igbo',
	'id': 'indonesian',
	'ga': 'irish',
	'it': 'italian',
	'ja': 'japanese',
	'jw': 'javanese',
	'kn': 'kannada',
	'kk': 'kazakh',
	'km': 'khmer',
	'ko': 'korean',
	'ku': 'kurdish (kurmanji)',
	'ky': 'kyrgyz',
	'lo': 'lao',
	'la': 'latin',
	'lv': 'latvian',
	'lt': 'lithuanian',
	'lb': 'luxembourgish',
	'mk': 'macedonian',
	'mg': 'malagasy',
	'ms': 'malay',
	'ml': 'malayalam',
	'mt': 'maltese',
	'mi': 'maori',
	'mr': 'marathi',
	'mn': 'mongolian',
	'my': 'myanmar (burmese)',
	'ne': 'nepali',
	'no': 'norwegian',
	'or': 'odia',
	'ps': 'pashto',
	'fa': 'persian',
	'pl': 'polish',
	'pt': 'portuguese',
	'pa': 'punjabi',
	'ro': 'romanian',
	'ru': 'russian',
	'sm': 'samoan',
	'gd': 'scots gaelic',
	'sr': 'serbian',
	'st': 'sesotho',
	'sn': 'shona',
	'sd': 'sindhi',
	'si': 'sinhala',
	'sk': 'slovak',
	'sl': 'slovenian',
	'so': 'somali',
	'es': 'spanish',
	'su': 'sundanese',
	'sw': 'swahili',
	'sv': 'swedish',
	'tg': 'tajik',
	'ta': 'tamil',
	'te': 'telugu',
	'th': 'thai',
	'tr': 'turkish',
	'uk': 'ukrainian',
	'ur': 'urdu',
	'ug': 'uyghur',
	'uz': 'uzbek',
	'vi': 'vietnamese',
	'cy': 'welsh',
	'xh': 'xhosa',
	'yi': 'yiddish',
	'yo': 'yoruba',
	'zu': 'zulu'}}

chatter = False

import random
import re
import os
from dotenv import load_dotenv
import PIL
import urllib.parse, urllib.request

import animec
from animec import *
load_dotenv()

from typing import List, Union, Optional

def get_affirmation():
	return requests.get("https://www.affirmations.dev/").json()["affirmation"]

def get_advice():
	return requests.get("https://api.adviceslip.com/advice").json()["slip"]["advice"]

input = namedtuple("input", ["content", "picture"])

API_KEY = '336d22fbad9d8795237e2abee2d4c32a'

search_api = 'AIzaSyAg2mp9Gv5UlGnLllDm8qrMI6szjyRuCYo'

class paginator:
	def __init__(self, ctx, **kwargs):
		self.embeds = None
		self.ctx = ctx
		self.bot = ctx.bot
		self.timeout = int(kwargs.pop("timeout", 60))
		self.current_page = 0
		self.emojis = []
		self.commands = []
		self.footer = kwargs.pop("footer", False)
		self.remove_reactions = True
		self.two_way_reactions = kwargs.pop("two_way_reactions", True)
		self.msg = None
		self.clear()

	def clear(self):
		self.emojis = []
		self.commands = []
		self.current_page = 0

	def add_reaction(self, emoji, command: str):
		self.emojis.append(emoji)
		self.commands.append(command)

	def insert_reaction(self, index: int, emoji, command: str):
		self.emojis.insert(index, emoji)
		self.commands.insert(index, command)

	def remove_reaction(self, emoji):
		for emoji in self.emojis:
			index = self.emojis.index(emoji)
			self.emojis.remove(emoji)
			self.commands.pop(index)

	def remove_reaction_at(self, index):
		if index > len(self.emojis) - 1 or index == -1:
			index = len(self.emojis) - 1
		elif index < 0:
			index = 0
		try:
			self.emojis.pop(index)
			self.commands.pop(index)
		except:
			pass

	async def clear_msg_reactions(self, msg):
		try:
			await msg.clear_reactions()
		except (discord.HTTPException, discord.Forbidden):
			for emoji in self.emojis:
				try:
					await msg.clear_reaction(emoji)
				except (discord.HTTPException, discord.Forbidden):
					try:
						await msg.remove_reaction(emoji, self.ctx.bot.user)
					except (discord.HTTPException, discord.Forbidden):
						pass

	async def remove_msg_reaction(self, msg, emoji, user):
		try:
			await msg.remove_reaction(emoji, user)
		except (discord.HTTPException, discord.Forbidden):
			pass

	async def wait_for(self, msg, check, timeout):
		if self.two_way_reactions:
			done, pending = await asyncio.wait([
				self.ctx.bot.wait_for(
					"reaction_add", check=check),
				self.ctx.bot.wait_for(
					"reaction_remove", check=check)
			], return_when=asyncio.FIRST_COMPLETED, timeout=timeout)
			if not done:
				raise asyncio.TimeoutError
			try:
				reaction, user = done.pop().result()
			except asyncio.TimeoutError:
				await self.clear_msg_reactions(msg)
				self.clear()
			for future in done:
				future.exception()
			for future in pending:
				future.cancel()

			return reaction, user
		else:
			try:
				reaction, user = await self.ctx.bot.wait_for(
					"reaction_add", check=check, timeout=timeout)
			except asyncio.TimeoutError:
				await self.clear_msg_reactions(msg)
				self.clear()
			else:
				return reaction, user

	async def edit(self, msg, emoji, user, embed=None, file=None):
		if self.remove_reactions:
			await self.remove_msg_reaction(msg, emoji, user)
		if embed:
			await msg.edit(embed=embed, file=file)
		else:
			await msg.edit(embed=(self.embeds[self.current_page].content.set_footer(text=f"{self.current_page + 1}/{len(self.embeds)}", icon_url=user.avatar.url)) if self.footer else self.embeds[self.current_page].content)

	async def send(self, embeds: List[input], send_to: Optional[Union[commands.Context, discord.Member, discord.User]] = None):
		self.embeds = embeds

		def check(reaction, user):
			return user == wait_for and reaction.message.id == self.msg.id and str(reaction.emoji) in [*self.emojis, "\U000023f9"]

		send_to = send_to or self.ctx

		wait_for = self.ctx.author if send_to == self.ctx else send_to

		if len(self.embeds) == 0:
			return

		if len(self.embeds) == 1:
			try:
				self.msg = await send_to.send(embed=self.embeds[0].content, file=self.embeds[0].picture)
				await self.msg.add_reaction("\U000023f9")
				r, u = await self.bot.wait_for("reaction_add", check=check)
				if str(r.emoji) == "\U000023f9":
					await self.msg.delete()
					return
			except Exception as e:
				await self.ctx.send(e)

		self.current_page = 0

		if self.footer:
			self.embeds[0].content.set_footer(
				text=f"{self.current_page + 1}/{len(self.embeds)}", icon_url=wait_for.avatar.url)

		self.msg = await send_to.send(embed=self.embeds[0].content, file=self.embeds[0].picture)

		for emoji in self.emojis:
			await self.msg.add_reaction(emoji)
			await asyncio.sleep(0.25)

		self.msg = await self.msg.channel.fetch_message(self.msg.id)

		navigating = True

		while navigating:
			if self.timeout > 0:
				try:
					reaction, user = await self.wait_for(self.msg, check, self.timeout)
				except (TypeError, asyncio.TimeoutError):
					await self.clear_msg_reactions(self.msg)
					navigating = False
			else:
				try:
					reaction, user = await self.wait_for(self.msg, check, None)
				except (TypeError, asyncio.TimeoutError):
					await self.clear_msg_reactions(self.msg)
					navigating = False

			try:
				index = self.emojis.index(reaction.emoji)

				command = self.commands[index]
			except:
				pass
			else:
				if command == "first":
					self.current_page = 0
					await self.edit(self.msg, reaction.emoji, user)

				elif command == "back":
					if self.current_page == 0:
						pass
					else:
						self.current_page -= 1
					await self.edit(self.msg, reaction.emoji, user)

				elif command in ["lock", "clear", "stop"]:
					await self.clear_msg_reactions(self.msg)
					navigating = False

				elif command == "delete":
					await self.msg.delete()
					await self.ctx.message.add_reaction("\U00002705")
					navigating = False

				elif command == "next":
					if self.current_page == len(self.embeds) - 1:
						pass
					else:
						self.current_page += 1
					await self.edit(self.msg, reaction.emoji, user)

				elif command == "last":
					self.current_page = len(self.embeds) - 1
					await self.edit(self.msg, reaction.emoji, user)

				elif command == "info":
					embed = discord.embed(title="Info", description="Seems like you stumbled upon the help page! Use the arrows below to move around the menu!",
										  colour=self.bot.neutral_embed_colour).set_footer(text=f"Requested by {wait_for.name}#{wait_for.discriminator}", icon_url=user.avatar.url)
					await self.edit(self.msg, emoji, user, embed)

				elif command == "number":
					def msgcheck(m):
						return m.author.id == wait_for.id and m.content in range(1, len(self.embeds))

					choice_msg = await send_to.send("What page do you want to go to?")

					m = await self.ctx.bot.wait_for("message", check=msgcheck, timeout=self.timeout or None)

					self.current_page = int(m.content) - 1
					await choice_msg.delete()
					await self.edit(self.msg, reaction.emoji, user)

				elif command == "delete":
					await self.msg.delete()
					await self.ctx.message.add_reaction("\U0001f44d")
					navigating = False

class quickpaginator(paginator):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.add_reaction("\U000023ea", "first")
		self.add_reaction("\U000025c0", "back")
		self.add_reaction("\U0001f5d1", "delete")
		self.add_reaction("\U000025b6", "next")
		self.add_reaction("\U000023e9", "last")

app_id = os.getenv("WOLFRAM_APP_ID")

def get_reddit():
	# get the credentials of the reddit user & bot
	reddit = praw.Reddit(
		user_agent=os.getenv('REDDIT_USER_AGENT'),
		username=os.getenv("REDDIT_USERNAME"),
		password=os.getenv("REDDIT_PASSWORD"),
		client_id=os.getenv("REDDIT_CLIENT_ID"), 
		client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
	)
	return reddit

reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
					 client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
					 username=os.getenv("REDDIT_USERNAME"),
					 password=os.getenv("REDDIT_PASSWORD"),
					 user_agent=os.getenv('REDDIT_USER_AGENT'))
spaceapi = os.getenv("SPACE_API_KEY")
api_key = os.getenv("TV_API")

class API(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@commands.command()
	async def sub(self, ctx, *, sub):
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://www.reddit.com/r/{sub}/hot.json") as response:
				j = await response.json()

		data = j["data"]["children"][random.randint(0, 25)]["data"]
		image_url = data["url"]
		title = data["title"]
		em = discord.Embed(title=title, color=discord.Color.random())
		em.set_image(url=image_url)
		em.set_footer(text=f"Requested by {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=em)

	@commands.command(name='meme')
	@commands.bot_has_permissions(embed_links=True)
	async def meme(self, ctx):
		'''
		Random meme generator.
		'''
		link = "https://memes.blademaker.tv/api?lang=en"
		async with aiohttp.ClientSession() as session:
			async with session.get(link) as response:
				if response.status == 200:
					res = await response.json()
				else:
					return
		title = res['title']
		ups = res["ups"]
		downs = res["downs"]
		sub = res["subreddit"]

		embed = discord.Embed(title=f'{title}', discription=f"{sub}", timestamp=datetime.datetime.utcnow())
		embed.set_image(url = res["image"])
		embed.set_footer(text=f"Upvote(s): {ups} | Downvote(s): {downs}") 

		await ctx.send(embed=embed)
	
	@commands.command()
	async def search(self, ctx, *args):
		'''Search using Wolfram Alpha'''
		query = '+'.join(args)
		url = f"https://api.wolframalpha.com/v1/result?appid={app_id}&i={query}%3F"
		response = requests.get(url)

		if response.status_code == 501:
			await ctx.send("`Not an understandable query...`")
			return

		elif response.text == 'an empty list':
			await ctx.send("`Not an understandable query...`")

		else:
			if query.startswith('hex+of'):
				await ctx.send(f"{response.text}")
			else:
				await ctx.send(f"`{response.text}`")

	@commands.command()
	async def reddit(self, ctx, *, subreddit):
		'''Gets posts from Reddit'''
		subreddit = reddit.subreddit(subreddit)
		all_subs = []
		hot = subreddit.new(limit=30)
		for submission in hot:
			print(submission)
			all_subs.append(submission)


		random_sub = random.choice(all_subs)
		name = random_sub.title
		em = discord.Embed(title=name)
		em.set_image(url=random_sub.url)
		em.add_field(name="Post URL", value=random_sub.url)
		em.add_field(name='Post Link',
						value=f"https://reddit.com{random_sub.permalink}")
		await ctx.send(embed=em)

	@commands.command(aliases=['tv'])
	async def tvname(self, ctx, *, query):
		'''Get info about any movie or TV show using the OMDB API.'''
		url = f"http://www.omdbapi.com/?apikey={api_key}&t={query}&plot=full"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as r:
				info = await r.json()
				if info['Type'] == 'movie':
					embed = discord.Embed(
						title=info['Title'], description=info['Plot'], colour=discord.Color.random())
					embed.add_field(name='Age Rating', value=info['Rated'])
					embed.add_field(name='Genre', value=info['Genre'])
					embed.add_field(name='Released', value=info['Released'])
					embed.add_field(name='Box Office', value=info['BoxOffice'])
					embed.add_field(name='Director', value=info['Director'])
					embed.add_field(name='Country', value=info['Country'])
					embed.add_field(name='Language', value=info['Language'])
					embed.add_field(name='IMDb Rating', value=f"{info['imdbRating']}/10")
					embed.add_field(name='Metascore', value=f"{info['Metascore']}/100")
					embed.add_field(name='Awards', value=info['Awards'])
					embed.set_thumbnail(url=info['Poster'])
					embed.set_footer(text=info['Actors'])
					await ctx.send(embed=embed)
				elif info['Type'] == 'series':
					embed = discord.Embed(
						title=info['Title'], description=info['Plot'], colour=discord.Color.random())
					embed.add_field(name='Age Rating', value=info['Rated'])
					embed.add_field(name='Genre', value=info['Genre'])
					embed.add_field(name='Year', value=info['Year'])
					embed.add_field(name='Released', value=info['Released'])
					embed.add_field(name='Country', value=info['Country'])
					embed.add_field(name='Language', value=info['Language'])
					embed.add_field(name='Seasons', value=info['totalSeasons'])
					embed.add_field(name='IMDb Rating', value=f"{info['imdbRating']}/10")
					embed.add_field(name='Director', value=info['Director'])
					embed.add_field(name='Writer', value=info['Writer'])
					embed.add_field(name='Metascore', value=f"{info['Metascore']}/100")
					embed.add_field(name='Awards', value=info['Awards'])
					embed.set_thumbnail(url=info['Poster'])
					embed.set_footer(text=info['Actors'])
					await ctx.send(embed=embed)

	@commands.command()
	async def year(self, ctx, year):
		'''Get a fact about a year'''
		url = f"http://numbersapi.com/{year}/year?json"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as r:
				info = await r.json()
				await ctx.send(f"`{info['text']}`")

	@commands.command()
	async def date(self, ctx, month, date):
		'''Get a fact about a date'''
		url = f"http://numbersapi.com/{month}/{date}/date?json"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as r:
				info = await r.json()
		await ctx.send(f"{info['text']}")

	@commands.command()
	async def fact(self, ctx):
		'''a random fact'''
		result = randfacts.getFact()
		await ctx.send(f'`{result}`')

	@commands.command()
	async def nfact(self, ctx, no: int):
		'''Get a normal or mathematical fact about any number'''

		res = ['1', '2']
		num = (random.choice(res))

		if num == '1':
			async with aiohttp.ClientSession() as session:
				async with session.get(f'http://numbersapi.com/{no}?json') as resp:
					file = await resp.json()
					fact = file['text']
					await ctx.send(f"`{fact}`")

		else:
			async with aiohttp.ClientSession() as session:
				async with session.get(f'http://numbersapi.com/{no}/math?json') as resp:
					file = await resp.json()
					fact = file['text']
					await ctx.send(f"`{fact}`")

	@commands.command(aliases=['xkcd', 'com'])
	async def comic(self, ctx):
		'''Get a comic from xkcd.'''
		async with aiohttp.ClientSession() as session:
			async with session.get(f'http://xkcd.com/info.0.json') as resp:
				data = await resp.json()
				currentcomic = data['num']
		rand = random.randint(0, currentcomic)  # max = current comic
		async with aiohttp.ClientSession() as session:
			async with session.get(f'http://xkcd.com/{rand}/info.0.json') as resp:
				data = await resp.json()
		em = discord.Embed(color=discord.Color.purple())
		em.title = f"XKCD Number {data['num']}- \"{data['title']}\""
		em.set_footer(
			text=f"Published on {data['month']}/{data['day']}/{data['year']}")
		em.set_image(url=data['img'])
		await ctx.send(embed=em)

	@commands.command()
	async def pypi(self, ctx, pkg: str):
		url = f"https://pypi.org/pypi/{pkg}/json"
		async with ClientSession() as session:
			async with session.get(url) as resp:
				info = await resp.json()
				infos = info['info']
				embed = discord.Embed(title=pkg,description=f"Author : {infos['author']}",color = discord.Color.random())
				embed.add_field(name='Description',value = infos['summary'])
				embed.add_field(name="Author Email", value=infos["author_email"] or "Not Provided")
				embed.add_field(name="Version", value=infos["version"] or "Not Provided")
				embed.add_field(name="Python Version Required",value=infos["requires_python"] or "Not Provided")
				embed.add_field(name='Github',value=infos['home_page'])
				embed.add_field(name='Download Link',value=f"[{pkg}](https://pypi.org/project/{pkg})")

		await ctx.send(embed=embed)

	@commands.command(name='urbandictionary',aliases=["urban", "ub"])
	async def _urbandictionary(self, ctx, *, query):
		async with aiohttp.ClientSession() as cs:
			async with cs.get("http://api.urbandictionary.com/v0/define", params={"term": query}) as r:
				jsondata = await r.json()

		BRACKETS = re.compile(r"(\[(.+?)\])")

		if len(jsondata['list']) == 0:
			fembed = discord.Embed(title = 'Urban Dictionary Error', color = discord.Color.random())
			fembed.add_field(name='Not a valid word', value='Could not find any results.')
			return await ctx.send(embed = fembed)

		def repl(m):
			word = m.group(2)
			replaced = word.replace(' ', '%20')
			return f"[{word}](https://www.urbandictionary.com/define.php?term={replaced})"

		embeds = []
		for entry in jsondata["list"]:
			description = BRACKETS.sub(repl, entry["definition"])
			embed = discord.Embed(title=entry["word"], url=entry["permalink"], description=description, timestamp=discord.utils.parse_time(
				entry["written_on"][0:-1]), colour=discord.Color.random())
			numbers = len(jsondata['list'])
			sexer = BRACKETS.sub(repl, entry["example"])
			embed.add_field(name='Example:',value=sexer)
			embed.set_footer(text=f"By {entry['author']}")
			embeds.append(input(embed, None))

		pages = paginator(ctx, remove_reactions=True)
		pages.add_reaction("\U000023ea", "first")
		pages.add_reaction("\U000025c0", "back")
		pages.add_reaction("❌", "delete")
		pages.add_reaction("\U000025b6", "next")
		pages.add_reaction("\U000023e9", "last")
		await pages.send(embeds)

	@commands.command()
	async def weather(self, ctx,*,city: str=None):
		'''Get the weather of any place on Earth.'''
		city = city or 'dubai'
		city_name = city
		complete_url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}'
		response = requests.get(complete_url)
		x = response.json()
		if x["cod"] != "404":
			y = x["main"]
			current_temperature = y["temp"]
			current_temperature_celsiuis = str(round(current_temperature - 273.15))
			current_pressure = y["pressure"]
			current_humidity = y["humidity"]
			z = x["weather"]
			weather_description = z[0]["description"]
			embed = discord.Embed(title=f"Weather in {city_name}",color=ctx.guild.me.top_role.color)
			embed.add_field(name="Weather", value=f"**{weather_description}**", inline=False)
			embed.add_field(name="Temperature(°C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
			embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
			embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
			embed.set_thumbnail(url="https://wi-images.condecdn.net/image/doEYpG6Xd87/crop/2040/f/weather.jpg")
			embed.set_footer(text=f"Requested by {ctx.author.name}")
			await ctx.send(embed=embed)
		else:
			await ctx.send(f"`{city_name} is not a real city.`")

	@commands.command(name="anime")
	async def _anime(self, ctx, *, query):
		try:
			anime = animec.Anime(query)
		except:
			await ctx.send(embed = discord.Embed(description="`Cannot find that anime.`"))
			return
		
		embed = discord.Embed(title=anime.title_english, url = anime.url, description=f"{anime.description[:2000]}...", color=discord.Color.random())
		embed.add_field(name="Rating", value=f"{anime.rating}", inline=True)
		embed.add_field(name="Ranking", value=f"{anime.ranked}", inline=True)
		embed.add_field(name="Status", value=f"{anime.status}", inline=False)
		embed.add_field(name="Episodes", value=f"{anime.episodes}", inline=False)
		embed.set_image(url=anime.poster)
		await ctx.send(embed=embed)

	@commands.command(name="aninews")
	async def _anime_news(self, ctx):
		news = animec.aninews.Aninews(amount=5)
		embed = discord.Embed(title="Anime news",color=discord.Color.random())
		embed.add_field(name=news.titles[0], value=f"{news.description[0][:400]}... [Continue Reading]({news.links[0]})")
		embed.add_field(name=news.titles[1], value=f"{news.description[1][:300]}... [Continue Reading]({news.links[1]})")
		embed.add_field(name=news.titles[2], value=f"{news.description[2][:300]}... [Continue Reading]({news.links[2]})")
		embed.add_field(name=news.titles[3], value=f"{news.description[3][:200]}... [Continue Reading]({news.links[3]})")
		embed.add_field(name=news.titles[4], value=f"{news.description[4][:200]}... [Continue Reading]({news.links[4]})")
		await ctx.send(embed = embed)

	@commands.command()
	async def ytsearch(self,ctx,*,search):
		query_string = urllib.parse.urlencode({'search_query' : search})
		html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
		search_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())
		await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])

	@commands.command()
	async def galaxy(self, ctx, year=None, month=None, day=None):
		'''Get a image of the galaxy'''
		if year == None and month == None and day == None:
			url = f"https://api.nasa.gov/planetary/apod?api_key={spaceapi}&count=10"
		else:
			url = f"https://api.nasa.gov/planetary/apod?api_key={spaceapi}&date={year}-{month}-{day}"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as r:
				info = await r.json()
		await session.close()

		print('1')

		embeds = []
		
		for entry in info:
			embed = discord.Embed(title='NASA Image of the Day',
								  color=discord.Color.random())
			embed.add_field(name=entry['title'], value = entry['explanation'])
			embed.set_image(url=entry['hdurl'])
			embed.set_footer(text=entry['date'])
			
			embeds.append(input(embed, None))
		
		print('1')

		pages = paginator(ctx, remove_reactions=True)
		pages.add_reaction("\U000023ea", "first")
		pages.add_reaction("\U000025c0", "back")
		pages.add_reaction("❌", "delete")
		pages.add_reaction("\U000025b6", "next")
		pages.add_reaction("\U000023e9", "last")
		await pages.send(embeds)

	@commands.command()
	async def langs(self, ctx, language=None):
		embeds = []
		if language is None:
			for i in langsi['entries']:
				res = langsi['entries']
				embed = discord.Embed(title='Languages', color = discord.Color.random(), description = "{} - {}".format(i, res[f'{i}']))
				embeds.append(input(embed, None))

			pages = paginator(ctx, remove_reactions=True)
			pages.add_reaction("\U000023ea", "first")
			pages.add_reaction("\U000025c0", "back")
			pages.add_reaction("❌", "delete")
			pages.add_reaction("\U000025b6", "next")
			pages.add_reaction("\U000023e9", "last")
			await pages.send(embeds)
		else:
			res = langsi['entries']

			def get_key(val):
				for key, value in res.items():
					if val == value:
						return key

			embed = discord.Embed(title='Languages', color=discord.Color.random(), description="{} - {}".format(f'{language}', get_key('language')))
			embeds.append(input(embed, None))

			pages = paginator(ctx, remove_reactions=True)
			pages.add_reaction("\U000023ea", "first")
			pages.add_reaction("\U000025c0", "back")
			pages.add_reaction("❌", "delete")
			pages.add_reaction("\U000025b6", "next")
			pages.add_reaction("\U000023e9", "last")
			await pages.send(embeds)

def setup(bot):
	bot.add_cog(API(bot))
