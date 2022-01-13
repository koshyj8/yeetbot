import discord
from discord.ext import commands
import asyncio

import random
from random import choice

def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)


class Poll(commands.Cog):
    """Poll Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def choose(self, ctx, *options):
        await ctx.send(f"{random.choice(options)}\n**Brought to you by Pro-Choice Industries™️**")

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx, *, question):
        messages = [ctx.message]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        for i in range(20):
            messages.append(await ctx.send(f'`Type the poll options 1-by-1, then type !publish to start the poll.`'))

            try:
                entry = await self.bot.wait_for('message', timeout=15, check=lambda m: m.author == ctx.message.author)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(f'{ctx.prefix}publish'):
                break

            answers.append((to_emoji(i), entry.clean_content))

        answer = '\n'.join(
            f'{keycap}: {content}' for keycap, content in answers)
        embed = discord.Embed(title=f'{ctx.author} has started a poll',
                              description=f'{question}', color=discord.Color.random())
        embed.add_field(name='Options', value=answer)
        actual_poll = await ctx.send(embed=embed)
        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

    @commands.command()
    @commands.guild_only()
    async def quickpoll(self, ctx, *questions_and_choices: str):
        if len(questions_and_choices) < 3:
            return await ctx.send('`Please give a question, and atleast 2 options`')
        elif len(questions_and_choices) > 21:
            return await ctx.send('`Only a maximum of 20 choices`')

        question = questions_and_choices[0]
        choices = [(to_emoji(e), v)
                   for e, v in enumerate(questions_and_choices[1:])]

        body = "\n".join(f"{key}: {c}" for key, c in choices)
        embed = discord.Embed(title=f'{ctx.author} has started a poll',
                              description=f'{question}', color=discord.Color.random())
        embed.add_field(name='Options', value=body)
        poll = await ctx.send(embed=embed)
        for emoji, _ in choices:
            await poll.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Poll(bot))
