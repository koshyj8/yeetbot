
res = """import discord
import os
import asyncio
import random
import sqlite3
import string

from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()




class Start(discord.ui.View):
    def __init__(self, user: int):
        super().__init__(timeout=60)
        self.value = None
        self.user = user

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        if interaction.user.id == self.user:
            self.value = True
            self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button, interaction):
        if interaction.user.id == self.user:
            self.value = False
            self.stop()


class Pending(discord.ui.View):
    def __init__(self, users: list):
        super().__init__()
        self.user = users[0]
        self.users = users

    @discord.ui.button(label="Play", style=discord.ButtonStyle.primary)
    async def participate(self, button, interaction):
        if interaction.user.id not in self.users:
            self.user = interaction.user.id
            return await interaction.response.send_message('You have joined the game.', ephemeral=True)


class PlayerRoles(discord.ui.View):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data

    @discord.ui.button(label='Check your role.', style=discord.ButtonStyle.primary)
    async def check_role(self, button, interaction):
        embed = discord.Embed(title="Mafia", color=0x5865F2, description="")
        if interaction.user.id in self.data['doctor']:
            embed.description = "You are a 'doctor'. You can save a citizen from being killed by the mafia every night."
        elif interaction.user.id in self.data['police']:
            embed.description = "You are a 'police'. Every night you can check whether the selected user is a mafia or not."
        elif interaction.user.id in self.data['mafia']:
            embed.description = "You are the 'mafia'. You can kill one citizen every night."
        elif interaction.user.id in self.data['citizen']:
            embed.description = "You are a 'citizen'. Good luck."
        else:
            embed.description = "You are not in the game."
        return await interaction.response.send_message(embed=embed, ephemeral=True)


class RoleActivate(discord.ui.View):
    def __init__(self, bot, data: dict):
        super().__init__()
        self.data = data
        self.bot = bot

    @discord.ui.button(label='Do your job!', style=discord.ButtonStyle.primary)
    async def activate_role(self, button, interaction):
        embed = discord.Embed(title="Mafia", color=0x5865F2, description="")
        if interaction.user.id in self.data['dead']:
            embed.description = "You are dead, so you cannot use your abilities."
        elif interaction.user.id in self.data['citizen']:
            embed.description = "You are a citizen, you do not have any abilities"
        elif interaction.user.id in self.data['mafia']:
            embed.description = "Please select the user you want to kill."
            return await interaction.response.send_message(embed=embed, ephemeral=True,
                                                           view=UserSelectView(self.bot, self.data))
        elif interaction.user.id in self.data['doctor']:
            embed.description = "Please select a user to save."
            return await interaction.response.send_message(embed=embed, ephemeral=True,
                                                           view=UserSelectView(self.bot, self.data))
        elif interaction.user.id in self.data['police'] and self.data['day'] != 1:
            embed.description = "Please select a user to investigate."
            return await interaction.response.send_message(embed=embed, ephemeral=True,
                                                           view=UserSelectView(self.bot, self.data))
        else:
            embed.description = "You haven't joined the game."
        return await interaction.response.send_message(embed=embed, ephemeral=True)


class UserSelectView(discord.ui.View):
    def __init__(self, bot, data: dict, night: bool = True):
        super().__init__()
        self.add_item(UserSelect(bot, data, night))


class UserSelect(discord.ui.Select):
    def __init__(self, bot, data: dict, night: bool):
        self.data = data
        self.night = night
        self.users = [bot.get_user(u)
                      for u in data['users'] if u not in data['dead']]
        select_options = [discord.SelectOption(
            label=u.name) for u in self.users]
        if night is False:
            select_options.insert(0, discord.SelectOption(label='Skip'))
        super().__init__(placeholder="Please select a user.", min_values=1,
                         max_values=1, options=select_options)

    async def callback(self, interaction):
        if self.night is True:
            user = discord.utils.get(self.users, name=self.values[0])
            target = self.data['days'][self.data['day']]['night']

            if interaction.user.id in self.data['mafia']:
                if target['mafia'] and target['mafia'] != user.id:
                    embed = discord.Embed(title="Mafia", color=0x5865F2,
                                           description=f"The target of killing has been changed.")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                target['mafia'] = user.id

            elif interaction.user.id in self.data['doctor']:
                target['doctor'] = user.id

            elif interaction.user.id in self.data['police'] and not target['police']:
                target['police'] = user.id
                embed = discord.Embed(
                    title="Mafia", color=0x5865F2, description="")
                if user.id in self.data['mafia']:
                    embed.description = f"{user.mention} You are the mafia."
                else:
                    embed.description = f"{user.mention} You are not the mafia."
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="Mafia", color=0xED4245, description="You have already used the ability.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            vote = self.data['days'][self.data['day']]['day']
            embed = discord.Embed(
                title="Mafia", color=0x5865F2, description="")

            user = None
            if self.values[0] != 'Skip':
                user = discord.utils.get(self.users, name=self.values[0]).id

            if interaction.user.id not in vote['voted'] and user:
                vote['voted'].append(interaction.user.id)
                vote['votes'][user] += 1
                embed.description = f"<@{user}> I voted for you."
            elif interaction.user.id not in vote['voted'] and not user:
                vote['voted'].append(interaction.user.id)
                vote['votes']['Skip'] += 1
                embed.description = "You voted to skip voting."
            else:
                embed.description = "You have already voted."
            return await interaction.response.send_message(embed=embed, ephemeral=True)


class Vote(discord.ui.View):
    def __init__(self, bot, data: dict):
        super().__init__()
        self.bot = bot
        self.data = data

    @discord.ui.button(label='vote', style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        if interaction.user.id in self.data['dead']:
            embed = discord.Embed(
                title="Mafia", color=0xED4245, description="You are dead, so you cannot vote.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        elif interaction.user.id not in self.data['users']:
            embed = discord.Embed(
                title="Mafia", color=0xED4245, description="You cannot vote because you did not participate in the game.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title="Mafia", color=0x5865F2,
                               description="Please select the user to be killed by voting.")
        return await interaction.response.send_message(embed=embed, ephemeral=True,
                                                       view=UserSelectView(self.bot, self.data, night=False))


class VoteTime(discord.ui.View):
    def __init__(self, until: int, voted: list, users: list):
        super().__init__()
        self.until = until
        self.voted = voted
        self.users = users

    @discord.ui.button(label="Increase", style=discord.ButtonStyle.green)
    async def plus(self, button, interaction):
        if interaction.user.id not in self.voted and interaction.user.id in self.users:
            self.voted.append(interaction.user.id)
            self.until += 30
            embed = discord.Embed(title='Mafia', color=0x5865F2,
                                   description=f"{interaction.user.mention}You increased the time.")
            return await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title='Mafia', color=0xED4245,
                                   description="You have already increased your time or you have not joined the game.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Shorten", style=discord.ButtonStyle.red)
    async def minus(self, button, interaction):
        if interaction.user.id not in self.voted and interaction.user.id in self.users:
            self.voted.append(interaction.user.id)
            self.until -= 30
            embed = discord.Embed(title='Mafia', color=0x5865F2,
                                   description=f"{interaction.user.mention}You shortened the time.")
            return await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title='Mafia', color=0xED4245,
                                   description="You've already saved time or you haven't joined the game.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)


class Paginator(discord.ui.View):
    def __init__(self, ctx, data: dict):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.data = data
        self.page = 0
        self.value = None

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, button, interaction):
        if self.page > 0 and self.ctx.author.id == interaction.user.id:
            self.page -= 1
            self.value = True
        else:
            self.value = False

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, button, interaction):
        if self.page < len(self.data['days']) and self.ctx.author.id == interaction.user.id:
            self.page += 1
            self.value = True
        else:
            self.value = False

class MafiaGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        self.conn = sqlite3.connect(r'C:\Users\HP\Desktop\yeetbot\cogs\ecodb\data.db')
        self.cursor = self.conn.cursor()

    def pick(self, guild, m, p, d):
        def seq(value):
            count = 0
            for u in dummy:
                if value == u:
                    return count
                count += 1

        def select(num, role):
            for i in range(num):
                value = random.choice(dummy)
                users[role].append(value)
                del dummy[seq(value)]

        users = self.data[guild]
        dummy = users['users'][:]
        select(m, 'mafia')
        select(p, 'police')
        select(d, 'doctor')
        users['citizen'] = dummy

    async def end(self, winner, data, thread, msg):
        def gen():
            return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))

        embed = discord.Embed(title="Game Over!", color=0x5865F2, description='')
        if winner == 'citizen':
            embed.description = "All mafia are dead. Citizens Win!"
        else:
            embed.description = "All citizens died. The mafia has won."

        codes = [c[0] for c in self.cursor.execute('SELECT * FROM mafia').fetchall()]
        code = gen()
        while code in codes:
            code = gen()

        data['winner'] = winner
        self.cursor.execute(f'INSERT INTO mafia VALUES ("{code}", "{thread.guild.id}", "{str(data)}")')
        self.conn.commit()

        try:
            doctor = self.bot.get_user(data['doctor'][0]).mention
        except IndexError:
            doctor = '`does not exist`'

        embed.add_field(name="player",
                        value=f"Mafia: {', '.join([self.bot.get_user(m).mention for m in data['mafia']])}\n"
                              f"Police: {self.bot.get_user(data['police'][0]).mention}\n"
                              f"Doctor: {doctor}\n"
                              f"Citizen: {', '.join([self.bot.get_user(c).mention for c in data['citizen']])}\n\n"
                              f"This game`Replay {code}`You can view it again using the command.")

        await thread.purge(limit=None)
        await thread.send(embed=embed)
        await msg.edit(embed=embed)

        for u in data['users']:
            user = self.bot.get_user(u)
            await thread.parent.set_permissions(user, send_messages_in_threads=True)

        del self.data[thread.parent.id]
        await asyncio.sleep(60)
        await thread.delete()

    async def check_finish(self, ctx, dead):
        data = self.data[ctx.channel.id]
        for u in data['mafia']:
            if u == dead:
                data['mafia-count'] -= 1
                break

        if len(data['users']) - (data['mafia-count'] + len(data['dead'])) <= data['mafia-count']:
            return 'mafia'
        elif data['mafia-count'] == 0:
            return 'citizen'
        return False

    @commands.command(aliases=['Mafia'])
    async def mafia(self, ctx):
        try:
            self.data[ctx.channel.id]
        except KeyError:
            pass
        else:
            embed = discord.Embed(title="Mafia", color=0xED4245,
                                   description="There is already a game in progress on this channel.")
            return await ctx.reply(embed=embed)

        start_view = Start(user=ctx.author.id)
        start_embed = discord.Embed(title="Mafia", color=0x5865F2,
                                     description="Do you want to start the game?")
        start_msg = await ctx.reply(embed=start_embed, view=start_view)

        await start_view.wait()
        await start_msg.delete()
        embed = discord.Embed(title="Mafia", color=0xED4245,
                               description="Timed out. please try again.")

        if start_view.value is None:
            return await ctx.reply(embed=embed)

        if start_view.value is False:
            embed.description = "You canceled the game."
            return await ctx.reply(embed=embed)

        data = self.data[ctx.channel.id] = {}
        users = data['users'] = []
        data['mafia'], data['police'], data['doctor'], data['citizen'], data['dead'] = [], [], [], [], []
        users.append(ctx.author.id)
        pending_view = Pending(users=users)
        pending_embed = discord.Embed(title="Mafia", color=0x5865F2,
                                       description=f"{ctx.author.mention}You started playing mafia. "
                                                   f"If you wish to participate, please click the emoticon at the bottom of the message within 60 seconds.\n")
        pending_embed.add_field(
            name="Participant", value=f"`{len(users)} Players`")
        pending_msg = await ctx.send(embed=pending_embed, view=pending_view)
        now = datetime.timestamp(datetime.now())
        until = now + 60
        while now <= until:
            now = datetime.timestamp(datetime.now())
            if pending_view.user not in users:
                users.append(pending_view.user)
                pending_embed.set_field_at(0, name="Participant", value=f"`{len(users)} Players`")
                await pending_msg.edit(embed=pending_embed)
            await asyncio.sleep(1)

        await pending_msg.delete()
        user_count = len(users)
        if user_count < 4:
            del self.data[ctx.channel.id]
            embed = discord.Embed(title="Mafia", color=0xED4245,
                                   description="The game was canceled due to insufficient number of players.")
            return await ctx.reply(embed=embed)

        if user_count >= 24:
            del self.data[ctx.channel.id]
            embed = discord.Embed(title="Mafia", color=0xED4245,
                                   description="The game has been canceled due to overcrowding.")
            return await ctx.reply(embed=embed)

        part_embed = discord.Embed(title="Mafia", color=0x5865F2,
                                    description=f"`{len(users)}A person will participate in the game."
                                                f"\nParticipant: {', '.join([f'<@{u}>' for u in users])}\n\n"
                                                f"After a while the game will start.")
        part_msg = await ctx.reply(' '.join([f'<@{u}>' for u in users]), embed=part_embed)
        thread = await part_msg.create_thread(name='Mafia', auto_archive_duration=60)
        await thread.trigger_typing()
        await asyncio.sleep(3)

        if user_count == 4:
            self.pick(ctx.channel.id, 1, 1, 0)
        elif user_count == 5:
            self.pick(ctx.channel.id, 1, 1, 1)
        elif user_count in [6, 7]:
            self.pick(ctx.channel.id, 2, 1, 1)
        else:
            self.pick(ctx.channel.id, 3, 1, 1)

        roles_embed = discord.Embed(title="A job has been assigned.", color=0x5865F2,
                                     description=f"Mafia: `{len(data['mafia'])} Players`\n"
                                                 f"police: `{len(data['police'])} Players`\n"
                                                 f"doctor: `{len(data['doctor'])} Players`\n"
                                                 f"citizen: `{len(data['citizen'])} Players`\n"
                                                 f"\nClick the button at the bottom of the message to confirm your job.\n"
                                                 f"After 20 seconds, it becomes the first night.")
        await thread.send(embed=roles_embed, view=PlayerRoles(data))
        await asyncio.sleep(20)
        await thread.purge(limit=None)
        data['mafia-count'] = len(data['mafia'])
        data['day'] = 1
        data['days'] = {}
        data['days'][1] = {'day': {}, 'night': {}}

        while True:
            for u in users:
                user = self.bot.get_user(u)
                await ctx.channel.set_permissions(user, send_messages_in_threads=False)

            turn_night_embed = discord.Embed(
                title='Mafia', color=0x5865F2, description=f"It's night.")
            await thread.send(embed=turn_night_embed)
            await asyncio.sleep(0.5)

            if data['day'] == 20:
                del self.data[ctx.channel.id]
                embed = discord.Embed(title="Mafia", color=0xED4245,
                                       description="The game was abnormally long and forced to quit.")
                return await ctx.reply(embed=embed)

            target = data['days'][data['day']]['night']
            target['mafia'], target['police'], target['doctor'], target['died'] = 0, 0, 0, 0

            night_embed = discord.Embed(title=f"{data['day']}day - night", color=0x5865F2,
                                         description=f"Please use the ability by clicking the button at the bottom of the message.\n"
                                                     f"\nafter 30 seconds {data['day'] + 1}It will be the first day.")
            night_msg = await thread.send(embed=night_embed, view=RoleActivate(self.bot, data))
            await asyncio.sleep(30)
            await night_msg.delete()
            data['day'] += 1

            turn_day_embed = discord.Embed(title='Mafia', color=0x5865F2, description=f"It was day.")
            await thread.send(embed=turn_day_embed)
            await asyncio.sleep(0.5)

            dead_embed = discord.Embed(title=f"{data['day']}primary - day", color=0x5865F2, description='')
            if not target['mafia'] or target['doctor'] == target['mafia']:
                dead_embed.description = "No one died."
            else:
                target['died'] = target['mafia']
                data['dead'].append(target['mafia'])
                dead_embed.description = f"<@{target['mafia']}>You have died."
            await thread.send(embed=dead_embed)

            check = await self.check_finish(ctx, target['mafia'])
            if check:
                return await self.end(check, data, thread, part_msg)

            data['days'][data['day']] = {'day': {}, 'night': {}}

            for u in data['users']:
                if u in data['dead']:
                    continue
                await ctx.channel.set_permissions(self.bot.get_user(u), send_messages_in_threads=True)

            vote = data['days'][data['day']]['day']
            now = datetime.timestamp(datetime.now())
            until = int(now) + 120
            time_voted = vote['time-voted'] = []
            time_view = VoteTime(until, time_voted, data['users'])

            day_embed = discord.Embed(title=f"{data['day']}primary - day", color=0x5865F2,
                                       description=f"1You will be given 120 seconds of free discussion time.\n"
                                                   f"You can increase/decrease the time by pressing the button at the bottom of the message.")
            day_embed.add_field(name="Time remaining", value=f"<t:{until}:R>")
            day_msg = await thread.send(embed=day_embed, view=time_view)

            while now <= until:
                now = datetime.timestamp(datetime.now())
                if time_view.until != until:
                    until = time_view.until
                    day_embed.set_field_at(0, name="Time remaining", value=f"<t:{until}>")
                    await day_msg.edit(embed=day_embed)
                await asyncio.sleep(1)

            await day_msg.delete()

            vote['voted'], vote['votes'], vote['died'] = [], {}, 0
            vote['votes']['Skip'] = len(data['users']) - len(data['dead'])
            for u in [u for u in data['users'] if u not in data['dead']]:
                vote['votes'][u] = 0

            vote_embed = discord.Embed(title=f"{data['day']}Primary - Voting", color=0x5865F2,
                                        description=f"Vote for 30 seconds to choose who you want to kill.")
            await thread.send(embed=vote_embed, view=Vote(self.bot, data))
            await asyncio.sleep(30)

            for v in vote['voted']:
                vote['votes']['Skip'] -= 1

            await thread.purge(limit=None)
            total = sorted(vote['votes'].items(), key=lambda k: k[1], reverse=True)
            vote_result = ''
            for t in total:
                name = t[0]
                if t[0] != 'Skip':
                    name = f'<@{t[0]}>'
                vote_result += f'{name}: `{t[1]}표`\n'

            vote_result_embed = discord.Embed(
                title=f"{data['day']}Primary - Voting Results", color=0x5865F2, description='')
            if total[0][1] == total[1][1] or total[0][0] == 'Skip':
                vote_result_embed.description = "No one died."
            else:
                vote['died'] = total[0][0]
                data['dead'].append(total[0][0])
                vote_result_embed.description = f"<@{total[0][0]}>You have died."
            vote_result_embed.add_field(
                name="voting result", value=vote_result)
            await thread.send(embed=vote_result_embed)

            check = await self.check_finish(ctx, total[0][0])
            if check:
                return await self.end(check, data, thread, part_msg)
            await asyncio.sleep(1)


def setup(bot):
    bot.add_cog(MafiaGame(bot))
"""

print(res.replace("\n",""))