from discord_slash import cog_ext, SlashContext
from animec import *
import animec
from typing import *
import asyncio
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
import random
import re
import os
from io import BytesIO
import urllib.parse
import urllib.request

from core.utils.pagin import paginator, quickpaginator

import sr_api
api = sr_api.Client(os.getenv("SR_API"))

from datetime import datetime

API_KEY = os.getenv('APIKEY')

search_api = os.getenv('SEARCH_API')

app_id = os.getenv("WOLFRAM_APP_ID")

reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                     username=os.getenv("REDDIT_USERNAME"),
                     password=os.getenv("REDDIT_PASSWORD"),
                     user_agent=os.getenv('REDDIT_USER_AGENT'))

spaceapi = os.getenv("SPACE_API_KEY")
api_key = os.getenv("TV_API")

class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sub(self, ctx: SlashContext, *, sub):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.reddit.com/r/{sub}/hot.json") as response:
                j = await response.json()

        data = j["data"]["children"][random.randint(0, 25)]["data"]
        image_url = data["url"]
        title = data["title"]
        em = discord.Embed(title=title, color=discord.Color.random())
        em.set_image(url=image_url)
        em.set_footer(
            text=f"Requested by {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def meme(self, ctx: SlashContext):
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

        embed = discord.Embed(
            title=f'{title}', discription=f"{sub}", timestamp=datetime.datetime.utcnow())
        embed.set_image(url=res["image"])
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
        em = discord.Embed(title=name, color=discord.Color.random())
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
                    embed.add_field(name='IMDb Rating',
                                    value=f"{info['imdbRating']}/10")
                    embed.add_field(name='Metascore',
                                    value=f"{info['Metascore']}/100")
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
                    embed.add_field(name='IMDb Rating',
                                    value=f"{info['imdbRating']}/10")
                    embed.add_field(name='Director', value=info['Director'])
                    embed.add_field(name='Writer', value=info['Writer'])
                    embed.add_field(name='Metascore',
                                    value=f"{info['Metascore']}/100")
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
                embed = discord.Embed(
                    title=pkg, description=f"Author : {infos['author']}", color=discord.Color.random())
                embed.add_field(name='Description', value=infos['summary'])
                embed.add_field(name="Author Email",
                                value=infos["author_email"] or "Not Provided")
                embed.add_field(
                    name="Version", value=infos["version"] or "Not Provided")
                embed.add_field(name="Python Version Required",
                                value=infos["requires_python"] or "Not Provided")
                embed.add_field(name='Github', value=infos['home_page'])
                embed.add_field(name='Download Link',
                                value=f"[{pkg}](https://pypi.org/project/{pkg})")

        await ctx.send(embed=embed)

    @commands.command()
    async def weather(self, ctx, *, city: str = None):
        '''Get the weather of any place on Earth.'''
        city = city or 'dubai'
        city_name = city
        complete_url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}'
        response = requests.get(complete_url)
        x = response.json()
        if x["cod"] != "404":
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature_celsiuis = str(
                round(current_temperature - 273.15))
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"].title()
            embed = discord.Embed(
                title=f"Weather in {city_name.title()}", color=discord.Color.random())
            embed.add_field(
                name="Weather", value=f"**{weather_description}**", inline=False)
            embed.add_field(
                name="Temperature(°C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
            embed.add_field(name="Humidity(%)",
                            value=f"**{current_humidity}%**", inline=False)
            embed.add_field(name="Atmospheric Pressure(hPa)",
                            value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(
                url="https://wi-images.condecdn.net/image/doEYpG6Xd87/crop/2040/f/weather.jpg")
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"`{city_name} is not a real city.`")

    @commands.command(name="anime")
    async def _anime(self, ctx, *, query):
        try:
            anime = animec.Anime(query)
        except:
            await ctx.send(embed=discord.Embed(description="`Cannot find that anime.`"))
            return

        embed = discord.Embed(title=anime.title_english, url=anime.url,
                              description=f"{anime.description[:2000]}...", color=discord.Color.random())
        embed.add_field(name="Rating", value=f"{anime.rating}", inline=True)
        embed.add_field(name="Ranking", value=f"{anime.ranked}", inline=True)
        embed.add_field(name="Status", value=f"{anime.status}", inline=False)
        embed.add_field(name="Episodes",
                        value=f"{anime.episodes}", inline=False)
        embed.set_image(url=anime.poster)
        await ctx.send(embed=embed)

    @commands.command(name="aninews")
    async def _anime_news(self, ctx):
        news = animec.aninews.Aninews(amount=5)
        embed = discord.Embed(title="Anime news", color=discord.Color.random())
        embed.add_field(
            name=news.titles[0], value=f"{news.description[0][:400]}... [Continue Reading]({news.links[0]})")
        embed.add_field(
            name=news.titles[1], value=f"{news.description[1][:300]}... [Continue Reading]({news.links[1]})")
        embed.add_field(
            name=news.titles[2], value=f"{news.description[2][:300]}... [Continue Reading]({news.links[2]})")
        embed.add_field(
            name=news.titles[3], value=f"{news.description[3][:200]}... [Continue Reading]({news.links[3]})")
        embed.add_field(
            name=news.titles[4], value=f"{news.description[4][:200]}... [Continue Reading]({news.links[4]})")
        await ctx.send(embed=embed)

    @commands.command()
    async def ytsearch(self, ctx, *, search):
        query_string = urllib.parse.urlencode({'search_query': search})
        html_content = urllib.request.urlopen(
            "https://www.youtube.com/results?" + query_string)
        search_results = re.findall(
            r"watch\?v=(\S{11})", html_content.read().decode())
        await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])

    @commands.command()
    async def galaxy(self, ctx, year = None, month = None, day = None):
        '''Get a image of the galaxy'''
        if year == None and month == None and day == None:
            url = f"https://api.nasa.gov/planetary/apod?api_key={spaceapi}&count=10"
        else:
            url = f"https://api.nasa.gov/planetary/apod?api_key={spaceapi}&date={year}-{month}-{day}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                info = await r.json()
        print(info['title'])

        print('1')

        embed = discord.Embed(title='NASA Image of the Day',
                                color=discord.Color.random())
        embed.add_field(name=info['title'], value=info['explanation'])
        embed.set_image(url=info['hdurl'])
        embed.set_footer(text=info['date'])


        await ctx.send(embed = embed)

    @commands.command()
    async def corona(self, ctx, category='Hot'):

        icon = {'Hot': '🔥',
                'New': '🆕',
                'Top': '🔝'}
        left = '⬅️'
        right = '➡️'
        reactions = [left, right]

        category = category.title()

        if category == 'Hot':
            submissions = list(reddit.subreddit('Coronavirus').hot(limit=5))
        elif category == 'New':
            submissions = list(reddit.subreddit('Coronavirus').new(limit=5))
        elif category == 'Top':
            submissions = list(reddit.subreddit('Coronavirus').top(limit=5))
        else:
            submissions = list(reddit.subreddit('Coronavirus').new(limit=5))

        index = 1

        description = f'{icon[category]} {category} Posts'
        timestamp = datetime.utcnow()
        url = 'https://www.reddit.com/r/Coronavirus/'
        embed = discord.Embed(title='/r/Coronavirus', description=description,
                              colour=discord.Colour.red(), timestamp=timestamp, url=url)

        for s in submissions:
            embed.add_field(name=f'⬆️ **{s.score}** | Posted by u/{s.author} on {datetime.fromtimestamp(s.created).strftime("%m/%d/%y %H:%M:%S")}',
                            value=f'[{s.title}](https://www.reddit.com{s.permalink})', inline=False)

        embed.set_thumbnail(
            url='https://styles.redditmedia.com/t5_2x4yx/styles/communityIcon_ex5aikhvi3i41.png')
        embed.set_footer(
            text=f'Requested by {ctx.message.author} • Page {index} of 3', icon_url=ctx.message.author.avatar_url)
        msg = await ctx.send(embed=embed)

        def predicate(message, l, r):
            def check(reaction, user):
                if reaction.message.id != message.id or user == self.bot.user:
                    return False
                if l and reaction.emoji == left and user == ctx.message.author:
                    return True
                if r and reaction.emoji == right and user == ctx.message.author:
                    return True
                return False
            return check

        while True:
            for reaction in reactions:
                await msg.add_reaction(reaction)
            l = index != 1
            r = index != 3
            try:
                react, self.user = await self.bot.wait_for('reaction_add', check=predicate(msg, l, r), timeout=120)
            except asyncio.TimeoutError:
                return

            if react.emoji == left and index > 1:
                index -= 1
                await msg.remove_reaction(left, self.user)
            elif react.emoji == right and index < 3:
                index += 1
                await msg.remove_reaction(right, self.user)

            embed.clear_fields()
            number = index * 5

            if category == 'Hot':
                submissions = list(reddit.subreddit(
                    'Coronavirus').hot(limit=15))[number-5:number]
            elif category == 'New':
                submissions = list(reddit.subreddit(
                    'Coronavirus').new(limit=15))[number-5:number]
            elif category == 'Top':
                submissions = list(reddit.subreddit(
                    'Coronavirus').top(limit=15))[number-5:number]

            for s in submissions:
                embed.add_field(name=f'⬆️ **{s.score}** | Posted by u/{s.author} on {datetime.fromtimestamp(s.created).strftime("%m/%d/%y %H:%M:%S")}',
                                value=f'[{s.title}](https://www.reddit.com{s.permalink})', inline=False)

            embed.set_footer(
                text=f'Requested by {ctx.message.author} • Page {index} of 3', icon_url=ctx.message.author.avatar_url)
            await msg.edit(embed=embed)

def setup(bot):
    bot.add_cog(API(bot))
