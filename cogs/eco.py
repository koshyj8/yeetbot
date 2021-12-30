import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
import aiosqlite
from random import *

class Economy(commands.Cog):
    """Economy which are related to economy! :D"""
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Economy are ready!')
        async with aiosqlite.connect("cogs\db\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS users (userid INTEGER, bank INTEGER, wallet INTEGER);")
                await connection.commit()

    @commands.command(aliases=['bal'])
    @cooldown(1, 5, BucketType.channel)
    async def balance(self, ctx, member : discord.Member= None):
        if member == None:
            member = ctx.author
        async with aiosqlite.connect("cogs\db\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM users WHERE userid = ?",(member.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(member.id,0,0))
                    await cursor.execute("SELECT * FROM users WHERE userid = ?",(member.id,))
                    rows = await cursor.fetchone()
                await connection.commit()
                em = discord.Embed(title = f"<:success:761297849475399710> {member.name}'s Balance", color = ctx.author.color)
                em.add_field(name = ":dollar: Wallet Balance:", value = f"{rows[2]} :coin:")
                em.add_field(name = ":bank: Bank Balance:", value = f"{rows[1]} :coin:")
                em.set_thumbnail(url = member.avatar_url)
                await ctx.send(embed=em)

    @commands.command(aliases=['dep'])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def deposit(self,ctx,amount = None):
        if amount == None:
            em = discord.Embed(title = "Deposit failed!", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "Specify an amount!")
            em.add_field(name = "Next Steps:", value = "Next time try to type an amount too!")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
            return

        if amount != "all" or amount != "max":
            amount = int(amount)

        async with aiosqlite.connect("cogs\db\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,0,''))
                else:
                    if amount != 'all' or amount != "max":
                        if amount > rows[1]:
                            em = discord.Embed(title = "Deposit failed!", color = ctx.author.color)
                            em.add_field(name = "Reason:", value = "You don't even have that much money!")
                            em.add_field(name = "Next Steps:", value = "Get richer next time!")
                            em.set_thumbnail(url = ctx.author.avatar_url)
                            await ctx.send(embed = em)
                            return
                        elif amount <= 0:
                            em = discord.Embed(title = "Deposit failed!", color = ctx.author.color)
                            em.add_field(name = "Reason:", value = "Amount was too low!")
                            em.add_field(name = "Next Steps:", value = "Type a positive integer next time!")
                            em.set_thumbnail(url = ctx.author.avatar_url)
                            await ctx.send(embed = em)
                            return
                        else:
                            await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] - amount,rows[0] + amount,ctx.author.id,))
                            em = discord.Embed(title = "<:success:761297849475399710> Deposit successful!", color = ctx.author.color)
                            em.add_field(name = ":bank: Amount Deposited:", value = f"{amount} :coin:")
                            em.set_thumbnail(url = ctx.author.avatar_url)
                            await ctx.send(embed = em)
                    else:
                        await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(0,rows[0] + rows[1],ctx.author.id,))
                        em = discord.Embed(title = "<:success:761297849475399710> Deposit successful!", color = ctx.author.color)
                        em.add_field(name = ":bank: Amount Deposited:", value = f"{rows[1]} :coin:")
                        em.set_thumbnail(url = ctx.author.avatar_url)
                        await ctx.send(embed = em)
                    await connection.commit()

    @commands.command(aliases=['with'])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def withdraw(self,ctx,amount = None):
        if amount == None:
            em = discord.Embed(title = "Withdraw failed!", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "Specify an amount!")
            em.add_field(name = "Next Steps:", value = "Next time try to type an amount too!")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
            return

        if not amount == 'all':
            amount = int(amount)
        async with aiosqlite.connect("cogs\db\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,0,))
                else:
                    if not amount == 'all':
                        if amount > rows[0]:
                            em = discord.Embed(title = "Withdraw failed!", color = ctx.author.color)
                            em.add_field(name = "Reason:", value = "You don't even have that much money!")
                            em.add_field(name = "Next Steps:", value = "Get richer next time!")
                            em.set_thumbnail(url = ctx.author.avatar_url)
                            await ctx.send(embed = em)
                            return
                        elif amount <= 0:
                            em = discord.Embed(title = "Withdraw failed!", color = ctx.author.color)
                            em.add_field(name = "Reason:", value = "Amount was too low!")
                            em.add_field(name = "Next Steps:", value = "Type a positive integer next time!")
                            em.set_thumbnail(url = ctx.author.avatar_url)
                            await ctx.send(embed = em)
                            return
                        else:
                            await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] + amount,rows[0] - amount,ctx.author.id,))
                            em = discord.Embed(title = "<:success:761297849475399710> Withdraw successful!", color = ctx.author.color)
                            em.add_field(name = ":dollar: Amount Withdrawn:", value = f"{amount} :coin:")
                            em.set_thumbnail(url = ctx.author.avatar_url)
                            await ctx.send(embed = em)
                    else:
                        await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] + rows[0],0,ctx.author.id,))
                        em = discord.Embed(title = "<:success:761297849475399710> Withdraw successful!", color = ctx.author.color)
                        em.add_field(name = ":dollar: Amount Withdrawn:", value = f"{rows[0]} :coin:")
                        em.set_thumbnail(url = ctx.author.avatar_url)
                        await ctx.send(embed = em)
                await connection.commit()

    @commands.command(aliases=['send', "share"])
    @commands.cooldown(1,30,commands.BucketType.user)
    async def give(self,ctx,member : discord.Member = None, amount = None):
        if amount == None:
            em = discord.Embed(title = "Give failed!", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "Specify an amount!")
            em.add_field(name = "Next Steps:", value = "Next time try to type an amount too!")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
            return
        if member is None:
            em = discord.Embed(title = "Give failed!", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "Mention a valid user.")
            em.add_field(name = "Next Steps:", value = "Next time try to type a valid member too!")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
            return

        amount = int(amount)
        
        async with aiosqlite.connect("cogs\db\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?", (ctx.author.id))
                bal = await cursor.fetchone()

                if not bal:
                    return await ctx.send("bruh, you've never even played-")

                if bal[1] < amount:
                    return await ctx.send("You don't even have that much money!")
                
                if amount == 0 or amount < 0:
                    await ctx.send("Amount must be positive!")
                    return
                
                em = discord.Embed(title = "<:success:761297849475399710> Give successful!", color = ctx.author.color)
                em.add_field(name = ":dollar: Amount Given:", value = f"{amount} :coin:")
                em.add_field(name ="Member:", value = f"{member.mention}")
                em.add_field(name = ":tada: Money:", value = "Give your money! :tada:")
                await ctx.send(embed = em)

                await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?", (bal[1] - amount, bal[0], ctx.author.id))
                await connection.commit()

        async with aiosqlite.connect("cogs\db\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?", (member.id))
                rows = await cursor.fetchone()

                await cursor.execute("UPDATE users SET wallet = ?, bank = ?, WHERE userid = ?", (rows[1] + amount, rows[0], member.id))
                await connection.commit()

    # error handling
    @give.error
    async def give_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = f"Command On Cooldown!", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Stop giving money it makes you poor!")
            em.add_field(name = "Try again in:", value = "{:.2f} seconds".format(error.retry_after))
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
        if isinstance(error, commands.BadArgument):
            em = discord.Embed(title = f"Error", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Arguments were of the wrong data type!")
            em.add_field(name = "Args", value = "```\nimp give <@user> <amount>\n```")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
        if isinstance(error, commands.MissingRequiredArgument):
            em = discord.Embed(title = f"Error", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"You didn't provide the right arguments!")
            em.add_field(name = "Args", value = "```\nimp give <@user> <amount>\n```")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)

    @withdraw.error
    async def withdraw_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = f"Command On Cooldown!", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = "You can always withdraw later idiot!")
            em.add_field(name = "Try again in:", value = "{:.2f} seconds".format(error.retry_after))
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
        if isinstance(error, commands.BadArgument):
            em = discord.Embed(title = f"Withdraw Error", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Arguments were of the wrong data type!")
            em.add_field(name = "Args", value = "```\nimp with <amount>\n```")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
        if isinstance(error, commands.MissingRequiredArgument):
            em = discord.Embed(title = f"Withdraw Error", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"You didn't provide the right arguments!")
            em.add_field(name = "Args", value = "```\nimp with <amount>\n```")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)


    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = f"Command On Cooldown!", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = "Check it later, money doesn't matter. Adding me to your server does \:D")
            em.add_field(name = "Try again in:", value = "{:.2f} seconds".format(error.retry_after))
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
        
        if isinstance(error, commands.BadArgument):
            em = discord.Embed(title = f"Balance Error", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Arguments were of the wrong data type!")
            em.add_field(name = "Args", value = "```\nimp balance [@user]\n```")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)


    @deposit.error
    async def deposit_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = f"Command On Cooldown!", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = "You can always deposit later idiot!")
            em.add_field(name = "Try again in:", value = "{:.2f} seconds".format(error.retry_after))
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
        if isinstance(error, commands.BadArgument):
            em = discord.Embed(title = f"Deposit Error", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Arguments were of the wrong data type!")
            em.add_field(name = "Args", value = "```\nimp deposit <amount>\n```")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)
        if isinstance(error, commands.MissingRequiredArgument):
            em = discord.Embed(title = f"Deposit Error", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"You didn't provide the right arguments!")
            em.add_field(name = "Args", value = "```\nimp dep <amount>\n```")
            em.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed = em)

    @commands.command()
    @commands.cooldown(1,15,commands.BucketType.user)
    async def beg(self, ctx):
        earnings = randint(
        1, 100
        )
        async with aiosqlite.connect("./data/economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,0))
                    await connection.commit()
                await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] + earnings, rows[0], ctx.author.id))
                rows = await cursor.fetchone()
                await connection.commit()
                em = discord.Embed(title = f"<:success:761297849475399710> {ctx.author.name} begs hard!", color = ctx.author.color)
                em.add_field(name = ":coin: Earnings", value = f"{earnings} :coin:", inline = False)
                em.set_thumbnail(url = ctx.author.avatar_url)
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                await ctx.send(embed=em)

    @commands.command()
    @commands.is_owner()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def devwith(self, ctx, amount = None):
        if amount is None:
            await ctx.send("Type an amount!")
            return
        if not amount == 'all':
            amount = int(amount)
        async with aiosqlite.connect("./data/economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,0,))
                else:
                    if not amount == 'all':
                        await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?", (rows[1] + amount, rows[0], ctx.author.id))
            await connection.commit()
        await ctx.send(f"Gave you {amount} :dollar:")

    @commands.command()
    @cooldown(1, 86400, BucketType.user)
    async def daily(self, ctx):
        earnings = 2000
        async with aiosqlite.connect("./data/economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,0))
                await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] + earnings, rows[0], ctx.author.id))
                rows = await cursor.fetchone()
                await connection.commit()
                em = discord.Embed(title = f"<:success:761297849475399710> {ctx.author.name} begs hard!", color = ctx.author.color)
                em.add_field(name = ":dollar: Earnings", value = f"{earnings} :coin:", inline = False)
                em.add_field(name = ":tada: Free prize:", value = "Once a day you can claim a free price!")
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                em.set_thumbnail(url = ctx.author.avatar_url)
                await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1,30,commands.BucketType.user)
    async def serve(self, ctx):
        earnings = randint(
        1, 500
        )
        async with aiosqlite.connect("./data/economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,0))
                await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] + earnings, rows[0], ctx.author.id))
                rows = await cursor.fetchone()
                await connection.commit()
                em = discord.Embed(title = f"<:success:761297849475399710> {ctx.author.name} serves their server!", color = ctx.author.color)
                em.add_field(name = ":coin: Earnings", value = f"{earnings} :coin:", inline = False)
                em.add_field(name = "Server:", value = f"{ctx.guild.name}")
                em.set_thumbnail(url = ctx.author.avatar_url)
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                await ctx.send(embed=em)


    @commands.command()
    @cooldown(1, 604800, BucketType.user)
    async def weekly(self, ctx):
        earnings = 15000
        async with aiosqlite.connect("./data/economy.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT bank, wallet FROM users WHERE userid = ?",(ctx.author.id,))
                rows = await cursor.fetchone()
                if not rows:
                    await cursor.execute("INSERT INTO users (userid, bank, wallet) VALUES (?,?,?)",(ctx.author.id,0,0))
                await cursor.execute("UPDATE users SET wallet = ?, bank = ? WHERE userid = ?",(rows[1] + earnings, rows[0], ctx.author.id))
                rows = await cursor.fetchone()
                await connection.commit()
                em = discord.Embed(title = f"<:success:761297849475399710> {ctx.author.name} begs hard!", color = ctx.author.color)
                em.add_field(name = ":dollar: Earnings", value = f"{earnings} :coin:", inline = False)
                em.add_field(name = ":tada: Free prize:", value = "Once a day you can claim a free price!")
                em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
                em.set_thumbnail(url = ctx.author.avatar_url)
                await ctx.send(embed=em)

    # Error handling with command handler!
    @serve.error
    async def serve_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = f"<:fail:761292267360485378> Slow it down C'mon", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Stop serving the server your in!")
            em.add_field(name = "Try again in:", value = "{:.2f} seconds".format(error.retry_after))
            em.set_thumbnail(url = ctx.author.avatar_url)
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = f"<:fail:761292267360485378> Slow it down C'mon", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Get back to studying!")
            seconds = round(error.retry_after)
            minutes = round(seconds / 60)
            hours = round(minutes / 60)
            em.add_field(name = "Try again in:", value = f"{hours} hours, {minutes} minutes and {seconds} seconds!")
            em.set_thumbnail(url = ctx.author.avatar_url)
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)

    @weekly.error
    async def weekly_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = f"<:fail:761292267360485378> Slow it down C'mon", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Get back to studying! Weekly prizes are called weekly for a reason!")
            em.add_field(name = "Try again in:", value = "{:.2f}s".format(error.retry_after))
            em.set_thumbnail(url = ctx.author.avatar_url)
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)

    @devwith.error
    async def devwith_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = f"<:fail:761292267360485378> Slow it down C'mon", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Your already too rich, Lord {ctx.author.mention}!")
            em.add_field(name = "Try again in:", value = "{:.2f} seconds".format(error.retry_after))
            em.set_thumbnail(url = ctx.author.avatar_url)
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)

    @beg.error
    async def beg_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = f"<:fail:761292267360485378> Slow it down C'mon", color = ctx.author.color)
            em.add_field(name = f"Reason:", value = f"Begging makes you look poor which you are {ctx.author.mention}!")
            em.add_field(name = "Try again in:", value = "{:.2f} seconds".format(error.retry_after))
            em.set_thumbnail(url = ctx.author.avatar_url)
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)

def setup(client):
    client.add_cog(Economy(client))