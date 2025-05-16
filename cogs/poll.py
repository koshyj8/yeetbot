import asyncio
import random
import discord
from discord.ext import commands


def to_emoji(index: int) -> str:
    base = 0x1F1E6
    return chr(base + index)


class Poll(commands.Cog):
    """Poll commands for creating and managing user polls."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="choose")
    async def choose(self, ctx: commands.Context, *options: str) -> None:
        """Randomly choose one option from the provided list."""
        if not options:
            await ctx.send("Please provide some options to choose from.")
            return
        choice = random.choice(options)
        await ctx.send(f"{choice}\n**Brought to you by Pro-Choice Industries™️**")

    @commands.command(name="poll")
    @commands.guild_only()
    async def poll(self, ctx: commands.Context, *, question: str) -> None:
        """Initiates an interactive poll with multiple options."""
        messages = [ctx.message]
        answers = []

        for i in range(20):
            prompt = await ctx.send(
                "`Type the poll options one-by-one, then type !publish to start the poll.`"
            )
            messages.append(prompt)

            try:
                entry = await self.bot.wait_for(
                    "message", timeout=15, check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(f"{ctx.prefix}publish"):
                break

            answers.append((to_emoji(i), entry.clean_content))

        if not answers:
            await ctx.send("Poll creation timed out or was canceled.")
            return

        options_text = '\n'.join(f"{emoji}: {text}" for emoji, text in answers)
        embed = discord.Embed(
            title=f"{ctx.author} has started a poll",
            description=question,
            color=discord.Color.random()
        )
        embed.add_field(name="Options", value=options_text)

        poll_message = await ctx.send(embed=embed)
        for emoji, _ in answers:
            await poll_message.add_reaction(emoji)

    @commands.command(name="quickpoll")
    @commands.guild_only()
    async def quickpoll(self, ctx: commands.Context, *args: str) -> None:
        """Creates a quick poll with the given question and up to 20 options."""
        if len(args) < 3:
            await ctx.send("`Please provide a question followed by at least 2 options.`")
            return
        elif len(args) > 21:
            await ctx.send("`Only a maximum of 20 choices allowed.`")
            return

        question, *choices_raw = args
        choices = [(to_emoji(i), option) for i, option in enumerate(choices_raw)]

        options_text = '\n'.join(f"{emoji}: {text}" for emoji, text in choices)
        embed = discord.Embed(
            title=f"{ctx.author} has started a poll",
            description=question,
            color=discord.Color.random()
        )
        embed.add_field(name="Options", value=options_text)

        poll_message = await ctx.send(embed=embed)
        for emoji, _ in choices:
            await poll_message.add_reaction(emoji)


async def setup(bot: commands.Bot):
    await bot.add_cog(Poll(bot))
