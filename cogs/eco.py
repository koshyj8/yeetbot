from core.utils.pagin import paginator, quickpaginator
import aiosqlite
import discord
from discord.ext import commands
import asyncio
import sqlite3
import time
import datetime
from datetime import datetime as dte
import random
from discord.ext.commands.converter import MemberConverter
from discord.ext import menus
import json

from pytz import timezone, utc


class LeaderboardMenu(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=5)

    async def format_page(self, menu, entries):
        embed = discord.Embed(
            title='🏆 Top 10 users 🏆', description='Sorted by the total of wallet and bank balance combined', color=discord.Color.random())
        place = 0

        for row in entries:
            place += 1
            user = row[0]
            embed.add_field(
                name=f'{user}', value=f"**Bank:** {row[1]}\n**Wallet:** {row[2]}\n**Total:** {row[1] + row[2]}", inline=False)
        return embed


class InventoryMenu(menus.ListPageSource):
    def __init__(self, data, user):
        self.user = user
        super().__init__(data, per_page=6)

    async def format_page(self, menu, entries):
        embed = discord.Embed(
            title=f"{self.user.name}'s Inventory", color=discord.Color.random())

        for row in entries:
            if row[2] and row[2] != 0:
                embed.add_field(
                    name=row[1], value=f"**Amount:** {row[2]}\n**ID:** {row[0]}")
        return embed


db = sqlite3.connect("database\eco.sqlite")
await_db = sqlite3.connect("database\eco.sqlite")


class Economy(commands.Cog):
    """ECONOMY COMMANDS"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['lb'], brief = "Economy Leaderboard")
    async def leaderboard(self, ctx):
        async with aiosqlite.connect('database\eco.sqlite') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT * FROM user')
                rows = await cursor.fetchall()
                await connection.commit()

        top = sorted(rows, reverse=True, key=lambda x: x[1] + x[2])[:10]
        top = [list(x) for x in top]
        place = 0

        for row in top:
            if place == 0:
                pl = f"🥇 "
            elif place == 1:
                pl = f"🥈 "
            elif place == 2:
                pl = f"🥉 "
            else:
                pl = ''
            top[place][0] = f'{pl}{place+1}. {await self.bot.fetch_user(row[0])}' or "User not found"
            place += 1

        pages = menus.MenuPages(source=LeaderboardMenu(
            top), delete_message_after=True)
        await pages.start(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        # Use the below line to debug if the cog stops working
        #print('Economy Cog is active on startup')
        async with aiosqlite.connect("database\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS shop (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price INTEGER, available BOOL);")
                await connection.commit()

    @commands.command(brief="Create an economy account")
    async def create(self, ctx):
        cursor = db.cursor()
        cursor.execute(
            f'SELECT member_id from user WHERE member_id = {ctx.author.id}')
        result = cursor.fetchone()

        if result is None:
            sql = ('INSERT INTO user(member_id, bank, wallet) VALUES(?,?,?)')
            val = (ctx.author.id, 1000, 500)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            await ctx.send("`You have successfully created an account.`")
        else:
            await ctx.send("`You already have an account.`")

    @commands.command(brief="Get a user's balance")
    async def bal(self, ctx, member: MemberConverter = None):
        member = member or ctx.author

        cursor = db.cursor()
        cursor.execute(
            f'SELECT member_id, bank, wallet FROM user WHERE member_id = {member.id}')
        result = cursor.fetchone()

        if result is None:
            return await ctx.send("`Please create an account first.`")

        embed = discord.Embed(
            title=f"{member.name}'s Balance", color=discord.Color.random())
        embed.add_field(name='Bank Balance', value=result[1])
        embed.add_field(name='Wallet', value=result[2])
        embed.add_field(name='Net Worth', value=result[2] + result[1])
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['dep'], brief="Deposit money to the bank")
    async def deposit(self, ctx, amount):
        cursor = db.cursor()
        cursor.execute(
            f'SELECT member_id, bank, wallet FROM user WHERE member_id = {ctx.author.id}')
        result = cursor.fetchone()

        if result is None:
            return await ctx.send("`Please create an account first.`")

        if amount == 'all':
            amount = result[2]

            newbank = result[1] + amount

            sql = (
                f"UPDATE user SET bank = {newbank}, wallet = {0} WHERE member_id = {ctx.author.id}")
            cursor.execute(sql)
            db.commit()
            cursor.close()

            await ctx.send(f"`Successfully deposited {amount} coins.`")

        elif int(amount) > result[2]:
            await ctx.send(f"`You do not have {amount} coins in your waller.`")

        elif (int(amount) <= result[2] and int(amount) != 0):
            amount = int(amount)
            newbank = result[1] + amount
            newwallet = result[2] - amount
            sql = (
                f"UPDATE user SET bank = {newbank}, wallet = {newwallet} WHERE member_id = {ctx.author.id}")
            cursor.execute(sql)
            db.commit()
            cursor.close()

            await ctx.send(f"`Successfully deposited {amount} coins.`")

        elif int(amount) == 0:
            await ctx.send("`Please specify an amount greater than 0.`")

        elif str(amount) != 'all':
            await ctx.send("`Please input an amount or use 'all'`")

    @commands.command(aliases=['wd', 'with'], brief="Withdraw money from hands")
    async def withdraw(self, ctx, amount):

        cursor = db.cursor()
        cursor.execute(
            f'SELECT member_id, bank, wallet FROM user WHERE member_id = {ctx.author.id}')

        result = cursor.fetchone()

        if result is None:
            return await ctx.send("`Please create an account first.`")

        if amount == 'all':
            amount = result[1]

            newwallet = result[2] + amount

            sql = (
                f"UPDATE user SET bank = {0}, wallet = {newwallet} WHERE member_id = {ctx.author.id}")
            cursor.execute(sql)
            db.commit()
            cursor.close()

            await ctx.send(f"`Successfully withdrew {amount} coins.`")

        elif int(amount) > result[1]:
            await ctx.send(f"`You do not have {amount} coins in the bank.`")

        elif (int(amount) <= result[1] and int(amount) != 0):
            amount = int(amount)
            newbank = result[1] - amount
            newwallet = result[2] + amount
            sql = (
                f"UPDATE user SET bank = {newbank}, wallet = {newwallet} WHERE member_id = {ctx.author.id}")
            cursor.execute(sql)
            db.commit()
            cursor.close()

            await ctx.send(f"`Successfully withdrew {amount} coins.`")

        elif int(amount) == 0:
            await ctx.send("`Please specify an amount greater than 0.`")

        elif str(amount) != 'all':
            await ctx.send("`Please input an amount or use 'all'`")

    @commands.command(brief="Daily allowance")
    async def daily(self, ctx):
        cursor = db.cursor()
        cursor.execute(
            f'SELECT last_daily, wallet, member_id FROM user WHERE member_id = {ctx.author.id}')
        result = cursor.fetchone()

        if result is None:
            return await ctx.send("`Please create an account first.`")

        if result[0] is None:

            sql = (
                f"UPDATE user SET last_daily = ?, wallet = ? WHERE member_id = {ctx.author.id}")
            wallet = result[1] + 2000
            pattern = '%Y.%m.%d %H:%M:%S'
            time_now = datetime.datetime.now()
            epoch = int(time.mktime(time.strptime(
                str(time_now).partition('.')[0].replace('-', '.'), pattern)))
            vals = (epoch, wallet)
            cursor.execute(sql, vals)
            db.commit()
            cursor.close()
            await ctx.send("`You have claimed your daily reward of 2000 coins.`")
        else:
            date_now = datetime.datetime.now()
            pattern = '%Y.%m.%d %H:%M:%S'
            epoch = int(time.mktime(time.strptime(
                str(date_now).partition('.')[0].replace('-', '.'), pattern)))

            if epoch - result[0] >= 86400:
                sql = (
                    f"UPDATE user SET last_daily = ?, wallet = ? WHERE member_id = {ctx.author.id}")
                vals = (epoch, result[1] + 2000)
                cursor.execute(sql, vals)
                db.commit()
                cursor.close()
                await ctx.send("`You have claimed your daily reward of 2000 coins`")
            else:
                await ctx.send("`Its a 'daily' command for a reason.`")

    @commands.command(brief="Weekly allowance")
    async def weekly(self, ctx):
        cursor = db.cursor()
        cursor.execute(
            f'SELECT last_weekly, wallet, member_id FROM user WHERE member_id = {ctx.author.id}')
        result = cursor.fetchone()

        if result is None:
            return await ctx.send("`Please create an account first.`")

        if result[0] is None:

            sql = (
                f"UPDATE user SET last_weekly = ?, wallet = ? WHERE member_id = {ctx.author.id}")
            wallet = result[1] + 10000
            pattern = '%Y.%m.%d %H:%M:%S'
            time_now = datetime.datetime.now()
            epoch = int(time.mktime(time.strptime(
                str(time_now).partition('.')[0].replace('-', '.'), pattern)))
            vals = (epoch, wallet)
            cursor.execute(sql, vals)
            db.commit()
            cursor.close()
            await ctx.send("`You have claimed your weekly reward.`")
        else:
            date_now = datetime.datetime.now()
            pattern = '%Y.%m.%d %H:%M:%S'
            epoch = int(time.mktime(time.strptime(
                str(date_now).partition('.')[0].replace('-', '.'), pattern)))

            if epoch - result[0] >= 604800:
                sql = (
                    f"UPDATE user SET (last_weekly, wallet) VALUES(?, ?) WHERE member_id = {ctx.author.id}")
                vals = (epoch, result[1] + 10000)
                cursor.execute(sql, vals)
                db.commit()
                cursor.close()
                await ctx.send("`You have claimed your weekly reward of 10000 coins.`")
            else:
                await ctx.send("`Its a 'weekly' command for a reason.`")

    @commands.command(brief="Work to earn money")
    async def work(self, ctx):
        cursor = db.cursor()
        cursor.execute(
            f"SELECT member_id, wallet, job, last_job FROM user WHERE member_id = {ctx.author.id}")
        result = cursor.fetchone()
        jobs = ['Cashier', 'Shop stocker', 'Realtor', 'Delivery Driver']
        job = random.choice(jobs)

        if result is None:
            return await ctx.send("`Please create an account first.`")

        if job == 'Cashier' or job == 'Delivery Driver':
            earnings = random.randint(500, 1000)
        elif job == 'Shop stocker':
            earnings = random.randint(300, 800)
        elif job == 'Realtor':
            earnings = random.randint(900, 1800)

        if result[2] is None:

            sql = (
                f"UPDATE user SET job = ?, last_job = ?, wallet = ? WHERE member_id = {ctx.author.id}")
            pattern = '%Y.%m.%d %H:%M:%S'
            time_now = datetime.datetime.now()

            epoch = int(time.mktime(time.strptime(
                str(time_now).partition('.')[0].replace('-', '.'), pattern)))
            val = (job, epoch, result[1] + earnings)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            await ctx.send(f"`You have been employed as a {job}\nYou worked and earned {earnings} coins.`")
        else:
            job = result[2]
            if job == 'Cashier' or job == 'Delivery Driver':
                earnings = random.randint(500, 1000)
            elif job == 'Shop stocker':
                earnings = random.randint(300, 800)
            elif job == 'Realtor':
                earnings = random.randint(900, 1800)
            date_now = datetime.datetime.now()
            pattern = '%Y.%m.%d %H:%M:%S'
            epoch = int(time.mktime(time.strptime(
                str(date_now).partition('.')[0].replace('-', '.'), pattern)))

            if epoch - result[3] >= 7200:
                sql = (
                    f"UPDATE user SET last_job = ?, wallet = ? WHERE member_id = {ctx.author.id}")
                vals = (epoch, result[1] + earnings)
                cursor.execute(sql, vals)
                db.commit()
                cursor.close()
                await ctx.send(f"`You worked as a {job} and earned {earnings} coins.`")
            else:
                await ctx.send(f"`You can only work every 2 hours.`")

    @commands.command(brief = "Rob a user")
    async def rob(self, ctx, *, user_to_rob: MemberConverter):
        pattern = '%Y.%m.%d %H:%M:%S'
        time_now = datetime.datetime.now()
        epoch = int(time.mktime(time.strptime(
                                str(time_now).partition('.')[0].replace('-', '.'), pattern)))

        cursor = db.cursor()
        cursor.execute(
            f"SELECT member_id, wallet, last_rob FROM user WHERE member_id = {ctx.author.id}")
        result_robber = cursor.fetchone()

        if result_robber is None:
            return await ctx.send("`Please create an account first.`")

        cursor.execute(
            f"SELECT member_id, wallet, last_robbed FROM user WHERE member_id = {user_to_rob.id}")
        result_robbed = cursor.fetchone()

        if result_robbed is None:
            return await ctx.send("`The person you are trying to rob does not have an account.`")

        random_rob = random.randint(1, 6)

        if result_robber[2] is not None and result_robbed[2] is None:
            print(result_robber[2])
            if result_robbed[1] > 800 and epoch - result_robber[2] >= 28800:
                if random_rob != 1 or random_rob != 6:
                    loot = random.randint(100, 1000)
                    sql = (
                        f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
                    val = (result_robber[1] + loot, epoch)
                    sql_r = (
                        f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
                    val_r = (result_robbed[1] - loot, epoch)
                    cursor.execute(sql, val)
                    cursor.execute(sql_r, val_r)
                    db.commit()
                    cursor.close()
                    await ctx.send(f"`You successfully robbed {user_to_rob.name} of {loot} coins.`")
                elif random_rob == 1:
                    await ctx.send(f"`You were unable to rob {user_to_rob.name}`")
                elif random_rob == 6:
                    loot = random.randint(100, result_robber[1])
                    sql = (
                        f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
                    val = (result_robber[1] - loot, epoch)
                    sql_r = (
                        f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
                    val_r = (result_robbed[1] + loot, epoch)
                    cursor.execute(sql, val)
                    cursor.execute(sql_r, val_r)
                    db.commit()
                    cursor.close()
                    await ctx.send(f"`You successfully robbed {user_to_rob.name} of {loot} coins.`")

            elif epoch - result_robber[2] < 28800:
                tz = timezone("Asia/Dubai")
                d = dte.fromtimestamp(result_robber[2], tz).strftime(
                    '%Y-%m-%d %H:%M:%S')
                await ctx.send((f"`You can only rob once every 8 hours. Your last heist took place at {d}`"))

        elif result_robber[2] is None and result_robbed[2] is not None:
            if result_robbed[1] > 800 and epoch - result_robbed[2] >= 43200:
                if random_rob != 1 or random_rob != 6:
                    loot = random.randint(100, 1000)
                    sql = (
                        f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
                    val = (result_robber[1] + loot, epoch)
                    sql_r = (
                        f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
                    val_r = (result_robbed[1] - loot, epoch)
                    cursor.execute(sql, val)
                    cursor.execute(sql_r, val_r)
                    db.commit()
                    cursor.close()
                    await ctx.send(f"`You successfully robbed {user_to_rob.name} of {loot} coins.`")
                elif random_rob == 1:
                    await ctx.send(f"`You were unable to rob {user_to_rob.name}`")
                elif random_rob == 6:
                    loot = random.randint(100, result_robber[1])
                    sql = (
                        f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
                    val = (result_robber[1] - loot, epoch)
                    sql_r = (
                        f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
                    val_r = (result_robbed[1] + loot, epoch)
                    cursor.execute(sql, val)
                    cursor.execute(sql_r, val_r)
                    db.commit()
                    cursor.close()
                    await ctx.send(f"`You got caught trying to steal from {user_to_rob.name} and have to pay him a fine of {loot} coins.`")
            elif epoch - result_robbed[2] < 43200:
                tz = timezone("Asia/Dubai")
                d = dte.fromtimestamp(result_robbed[2], tz).strftime(
                    '%Y-%m-%d %H:%M:%S')
                await ctx.send(f"`This user was robbed in last the last 12 hours, give them a break. They were robbed last at {d}`")

        elif result_robbed[2] is None and result_robber[2] is None:
            if result_robbed[1] > 800:
                if random_rob != 1 or random_rob != 6:
                    loot = random.randint(100, 1000)
                    sql = (
                        f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
                    val = (result_robber[1] + loot, epoch)
                    sql_r = (
                        f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
                    val_r = (result_robbed[1] - loot, epoch)
                    cursor.execute(sql, val)
                    cursor.execute(sql_r, val_r)
                    db.commit()
                    cursor.close()
                    await ctx.send(f"`You successfully robbed {user_to_rob.name} of {loot} coins.`")
                elif random_rob == 1:
                    await ctx.send(f"`You were unable to rob {user_to_rob.name}`")
                elif random_rob == 6:
                    loot = random.randint(100, result_robber[1])
                    sql = (
                        f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
                    val = (result_robber[1] - loot, epoch)
                    sql_r = (
                        f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
                    val_r = (result_robbed[1] + loot, epoch)
                    cursor.execute(sql, val)
                    cursor.execute(sql_r, val_r)
                    db.commit()
                    cursor.close()
                    await ctx.send(f"`You were caught trying to rob {user_to_rob.name} and you have to pay them a fine of {loot} coins.`")

        elif result_robbed[2] is not None and result_robber[2] is not None:
            if ((result_robbed[1] > 800) and (epoch - result_robbed[2] >= 43200) and (epoch - result_robber[2] >= 28800)):
                if random_rob != 1 or random_rob != 6:
                    loot = random.randint(100, 1000)
                    sql = (
                        f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
                    val = (result_robber[1] + loot, epoch)
                    sql_r = (
                        f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
                    val_r = (result_robbed[1] - loot, epoch)
                    cursor.execute(sql, val)
                    cursor.execute(sql_r, val_r)
                    db.commit()
                    cursor.close()
                    await ctx.send(f"`You successfully robbed {user_to_rob.name} of {loot} coins.`")
                elif random_rob == 1:
                    await ctx.send(f"`You were unable to rob {user_to_rob.name}.`")
                elif random_rob == 6:
                    loot = random.randint(100, result_robber[1])
                    sql = (
                        f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
                    val = (result_robber[1] - loot, epoch)
                    sql_r = (
                        f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
                    val_r = (result_robbed[1] + loot, epoch)
                    cursor.execute(sql, val)
                    cursor.execute(sql_r, val_r)
                    db.commit()
                    cursor.close()
                    await ctx.send(f"`You were caught trying to rob {user_to_rob.name} and you have to pay them a fine of {loot} coins.`")
            elif epoch - result_robber[2] < 28800:
                tz = timezone("Asia/Dubai")
                d = dte.fromtimestamp(result_robber[2], tz).strftime(
                    '%Y-%m-%d %H:%M:%S')
                await ctx.send((f"`You can only rob once every 8 hours. Your last heist took place at {d}`"))
            elif epoch - result_robbed[2] < 43200:
                tz = timezone("Asia/Dubai")
                d = dte.fromtimestamp(result_robbed[2], tz).strftime(
                    '%Y-%m-%d %H:%M:%S')
                await ctx.send(f"`This user was robbed in last the last 12 hours, give them a break. They were robbed last at {d}`")

    # TODO: Add inventory, shop, buy, sell, gambling etc.

    @commands.group(invoke_without_command=True, brief = "Shop-related commands")
    async def shop(self, ctx):
        async with aiosqlite.connect("database\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM shop WHERE available = ?", (True,))
                rows = await cursor.fetchall()
        embed = discord.Embed(
            title="Shop", description="Use the buy command to buy an item by its id", color=discord.Color.random())
        for row in rows:
            embed.add_field(
                name=row[1], value=f"**Cost**: {row[2]} \n**ID**: {row[0]}")
        await ctx.send(embed=embed)

    @shop.command(brief="Edit the price of an item", hidden = True)
    @commands.is_owner()
    async def edit(self, ctx, item_id, price):
        item_id = int(item_id)
        price = int(price)
        async with aiosqlite.connect("database\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("UPDATE shop SET price = ? WHERE id = ?", (price, item_id,))
                await connection.commit()
        await ctx.send(f"Successfully changed price of item `{item_id}` to `{price}`")

    @shop.command(brief="Approve an item for buying.", hidden = True)
    @commands.is_owner()
    async def enable(self, ctx, item_id):
        item_id = int(item_id)
        async with aiosqlite.connect("database\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM shop WHERE id = ? AND available = ?", (item_id, False,))
                rows = await cursor.fetchone()
                if rows:
                    await ctx.send(f"Successfully enabled item `{item_id}` in the shop")
                else:
                    await ctx.send("That item doesnt exist or is enabled")
                await cursor.execute("UPDATE shop SET available = ? WHERE id = ?", (True, item_id,))
                await connection.commit()

    @shop.command(brief="Remove an item from the shop", hidden = True)
    @commands.is_owner()
    async def remove(self, ctx, item_id):
        item_id = int(item_id)
        async with aiosqlite.connect("database\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM shop WHERE id = ? AND available = ?", (item_id, True,))
                rows = await cursor.fetchone()
                if rows:
                    await ctx.send(f"Successfully removed item `{item_id}` from the shop")
                else:
                    await ctx.send("That item doesnt exist")
                await cursor.execute("UPDATE shop SET available = ? WHERE id = ?", (False, item_id,))
                await connection.commit()

    @shop.command(brief = "Add an item to the shop")
    @commands.is_owner()
    async def add(self, ctx, name, price):
        price = int(price)
        async with aiosqlite.connect("database\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("INSERT INTO shop (name, price, available) VALUES (?,?,?)", (name, price, True,))
                await cursor.execute('SELECT id FROM shop')
                rows = await cursor.fetchall()
                number = rows[-1][0]
                await cursor.execute(f'ALTER TABLE user ADD COLUMN item{number} INTEGER;')
                await connection.commit()
        await ctx.send(f"Successfully added `{name}` to the shop at the price of `{price}`")

    @shop.command(brief="Buy an item from the shop")
    async def buy(self, ctx, item_id, amount=1):
        item_id, amount = int(item_id), int(amount)
        async with aiosqlite.connect("database\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT name, price FROM shop WHERE id = ? AND available = ?", (item_id, True,))
                row = await cursor.fetchone()
                await cursor.execute(f'SELECT item{item_id} FROM user WHERE member_id = {ctx.author.id}')
                row1 = await cursor.fetchone()
                await connection.commit()
        price, name = row[1] *amount, row[0]
        async with aiosqlite.connect("database\eco.sqlite") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT wallet FROM user WHERE member_id = ?", (ctx.author.id,))
                row = await cursor.fetchone()
                if row[0] >= price:
                    if row1[0]:
                        await cursor.execute(f"UPDATE user SET wallet = ?,item{item_id} = ? WHERE member_id = ?", (row[0] - price, row1[0] + amount, ctx.author.id,))
                        await connection.commit()
                        await ctx.send(f"`Successfully purchased {amount} {name}{'s' if amount > 1 else ''} for {price} coins.`")
                    else:
                        await cursor.execute(f"UPDATE user SET wallet = ?,item{item_id} = ? WHERE member_id = ?", (row[0] - price, amount, ctx.author.id,))
                        await connection.commit()
                        await ctx.send(f"`Successfully purchased {amount} {name}{'s' if amount > 1 else ''} for {price} coins.`")
                else:
                    await ctx.send("`You don't have enough coins.`")

    @commands.command(aliases=['inv'], brief = "Show a member's inventory")
    async def inventory(self, ctx, user: MemberConverter = None):
        user = user or ctx.author
        async with aiosqlite.connect('database\eco.sqlite') as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT id,name FROM shop')
                rows1 = await cursor.fetchall()
                amount = rows1[-1][0]
                rows = ','.join([f'item{x + 1}' for x in range(amount)])
                await cursor.execute(f'SELECT {rows} FROM user WHERE member_id = ?', (user.id,))
                row = await cursor.fetchone()
                await connection.commit()
            new_row = []
            for item in rows1:
                new = list(item)
                new.append(row[item[0] - 1])
                new_row.append(tuple(new))
            pages = menus.MenuPages(source=InventoryMenu(
                new_row, user), delete_message_after=True)
            await pages.start(ctx)

    @commands.command(aliases=['slots', 'bet'], brief = "Bet money and play slots")
    async def slot(self, ctx, bet: int):
        """ Roll the slot machine """
        emojis = "💎👑💫🌟🎰🍇🎱🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        slotmachine = f"** [{a} {b} {c}]\n{ctx.author.name}**,"

        if bet is None:
            await ctx.send("`Please enter an amount to bet.`")

        cursor = db.cursor()
        cursor.execute(
            f"SELECT wallet FROM user WHERE member_id = {ctx.author.id}")

        result = cursor.fetchone()

        if result is None:
            return await ctx.send("`Please create an account first.`")

        if (a == b == c):
            cursor.execute(
                f"UPDATE user SET wallet = {result[0] + (bet*3)} WHERE member_id = {ctx.author.id}")
            await ctx.send(f"{slotmachine} 3 IN A ROW!! WOW! ")
        elif (a == b) or (a == c) or (b == c):
            cursor.execute(
                f"UPDATE user SET wallet = {result[0] + (bet*2)} WHERE member_id = {ctx.author.id}")
            await ctx.send(f"{slotmachine} 2 IN A ROW!! GOOD JOB!  ")
        else:

            cursor.execute(
                f"UPDATE user SET wallet = {result[0] - (bet*2)} WHERE member_id = {ctx.author.id}")
            await ctx.send(f"{slotmachine} HA! YOU LOST! ")


def setup(bot):
    bot.add_cog(Economy(bot))
