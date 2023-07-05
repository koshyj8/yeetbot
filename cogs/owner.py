import datetime
import sys
from datetime import datetime
import os
import discord
import discordbotdash.dash as dbd
from cogwatch import watch
from discord.ext import commands
from discord.ext.commands.converter import MemberConverter


def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)

class Owner(commands.Cog):
    '''OWNER COMMANDS'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send(f'`Restarting Bot 🔃`')
        restart_bot()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print("\nCalled on_command_error")  # for
        print("ERROR: "+str(error)) 	     # debugging
        embed = discord.Embed(color=discord.Colour.from_rgb(255, 192, 203))

        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Error: Missing required argument(s). Try again. ⛔"
        await ctx.send(embed=embed)

    @commands.group(description='Changes the bot\'s status')
    @commands.is_owner()
    async def status(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('You missed one of the sub commands!')

    @status.command()
    async def offline(self, ctx):
        await self.bot.change_presence(status=discord.Status.invisible)
        await ctx.send('`Changing status!`')

    @status.command()
    async def online(self, ctx):
        await self.bot.change_presence(status=discord.Status.online)
        await ctx.send('`Changing status!`')

    @status.command(description='Changes the bot\'s streaming status.')
    @commands.is_owner()
    async def st(self, ctx, status, url):
        await self.bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Streaming(name=(status), url=url))
        await ctx.send(f'Bot has started streaming **{status}**.')

    @status.command(description='Changes the bot\'s listening status.')
    @commands.is_owner()
    async def l(self, ctx, *, status):
        await self.bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.listening, name=(status)))
        await ctx.send(f'Bot has started listening to **{status}**.')

    @status.command(description='Changes the bot\'s watching status.')
    @commands.is_owner()
    async def w(self, ctx, *, status):
        await self.bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.watching, name=(status)))
        await ctx.send(f'Bot has started watching **{status}**.')

    @status.command(description='Changes the bot\'s playing status.')
    @commands.is_owner()
    async def pl(self, ctx, *, status=None):
        if status == None:
            status = ''
        await self.bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(status))
        await ctx.send(f'Bot has started playing {status}.')

    @commands.command(description='Turns off the bot.')
    @commands.is_owner()
    async def shut(self, ctx):
        await ctx.send('`Bot going offline!`👋')
        await self.bot.change_presence(status=discord.Status.offline)
        await self.bot.close()
        exit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == "!help place":
            await message.channel.send("`This is the layout to place(similar to a phone dialpad)`\n:one::two::three:\n:four::five::six:\n:seven::eight::nine:")

    @commands.command()
    @commands.is_owner()
    async def toggle(self, ctx, *, command):
        '''Toggle On/Off a command'''
        command = self.bot.get_command(command)

        if command is None:
            await ctx.send("`I cant find that command.`")

        elif ctx.command == command:
            await ctx.send('`ur rly dumb arent u? tryna disable the toggle command`')

        else:
            command.enabled = not command.enabled
            ternary = "enabled" if command.enabled else "disabled"
            await ctx.send(f"`{command.qualified_name} command has been {ternary}`")

    @commands.command()
    @commands.is_owner()
    async def leaveguild(self, ctx, guild_id: int):
        '''Leave a Guild'''
        guild = self.bot.get_guild(guild_id)
        await ctx.send(f"`I'm leaving the server`:wave:")
        await guild.leave()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        channel = self.bot.get_channel(832858605744291862)
        if message.content.startswith(f'<@!'):
            await channel.send(f'`You got ghost-pinged by {message.author.name} at {current_time}`\n{message.content} by {message.author}')

    @commands.command()
    @commands.is_owner()
    async def rename(self, ctx, *, name):
        await self.bot.user.edit(username=name)
        await ctx.send(f"`Changed Bot Name to {name}`")

    @commands.command()
    @commands.is_owner()
    async def botavatar(self, ctx):
        attachment = ctx.message.attachments[0]
        b = await attachment.read()
        await self.bot.user.edit(avatar=b)
        await ctx.send(f"`Changed Bot Avatar`")

    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, member: MemberConverter, *, message):
        await ctx.message.delete()
        embeddm = discord.Embed(title=message)
        await member.send(embed=embeddm)

    @commands.Cog.listener()
    async def on_ready(self):
        dbd.openDash(self.bot)
        print('Good to Go!')
        print('Logged in as ---->', self.bot.user)
        print('ID:', self.bot.user.id)
        channel = self.bot.get_channel(792442544004923414)
        await self.bot.change_presence(status=discord.Status.online)
        await channel.send('`Hey There! I\'m Online!`')


async def setup(bot):
    await bot.add_cog(Owner(bot))
