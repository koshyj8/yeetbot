import discord
from discord.ext import commands
import sqlite3
import time
import datetime
import random
from discord.ext.commands.converter import MemberConverter

db = sqlite3.connect("database\eco.sqlite")

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command()
	async def create(self, ctx):
		cursor = db.cursor()
		cursor.execute(f'SELECT member_id from user WHERE member_id = {ctx.author.id}') 
		result = cursor.fetchone()
		date_time = datetime.datetime.now()


		if result is None:
			sql = ('INSERT INTO user(member_id, bank, wallet) VALUES(?,?,?)')
			val = (ctx.author.id,1000, 500)
			cursor.execute(sql, val)
			db.commit()
			cursor.close()
			await ctx.send("`You have successfully created an account.`")
		else:
			await ctx.send("`You already have an account.`")

	@commands.command()
	async def bal(self, ctx, member:MemberConverter=None):
		member = member or ctx.author

		cursor = db.cursor()
		cursor.execute(f'SELECT member_id, bank, wallet FROM user WHERE member_id = {member.id}')
		result = cursor.fetchone()

		if result is None:
			return await ctx.send("`Please create an account first.`")

		embed = discord.Embed(title = f"{member.name}'s Balance", color = discord.Color.random())
		embed.add_field(name = 'Bank Balance', value = result[1])
		embed.add_field(name = 'Wallet', value = result[2])
		embed.add_field(name = 'Net Worth', value = result[2] + result[1])
		embed.set_thumbnail(url = member.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(aliases = ['dep'])
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
			
			sql = (f"UPDATE user SET bank = {newbank}, wallet = {0} WHERE member_id = {ctx.author.id}")
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

	@commands.command(aliases = ['wd', 'with'])
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

	@commands.command()
	async def daily(self, ctx):
		cursor = db.cursor()
		cursor.execute(
			f'SELECT last_daily, wallet, member_id FROM user WHERE member_id = {ctx.author.id}')
		result = cursor.fetchone()

		if result is None:
			return await ctx.send("`Please create an account first.`")

		if result[0] is None:
	
			sql = (f"UPDATE user SET last_daily = ?, wallet = ? WHERE member_id = {ctx.author.id}")
			wallet = result[1] + 2000
			pattern = '%Y.%m.%d %H:%M:%S'
			time_now = datetime.datetime.now()
			epoch = int(time.mktime(time.strptime(
				str(time_now).partition('.')[0].replace('-','.'), pattern)))
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
				sql = (f"UPDATE user SET last_daily = ?, wallet = ? WHERE member_id = {ctx.author.id}")
				vals = (epoch, result[1] + 2000)
				cursor.execute(sql, vals)
				db.commit()
				cursor.close()
				await ctx.send("`You have claimed your daily reward of 2000 coins`")
			else:
				await ctx.send("`Its a 'daily' command for a reason.`")

	@commands.command()
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

	@commands.command()
	async def work(self, ctx):
		cursor = db.cursor()
		cursor.execute(f"SELECT member_id, wallet, job, last_job FROM user WHERE member_id = {ctx.author.id}")
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
			
			epoch = int(time.mktime(time.strptime(str(time_now).partition('.')[0].replace('-', '.'), pattern)))
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
				sql = (f"UPDATE user SET last_job = ?, wallet = ? WHERE member_id = {ctx.author.id}")
				vals = (epoch, result[1] + earnings)
				cursor.execute(sql, vals)
				db.commit()
				cursor.close()
				await ctx.send(f"`You worked as a {job} and earned {earnings} coins.`")
			else:
				await ctx.send(f"`You can only work every 2 hours.`")

	#TODO: Add rob, inventory, shop, buy, sell, gambling etc.

	@commands.command()
	async def rob(self, ctx, *, user_to_rob:MemberConverter):
		pattern = '%Y.%m.%d %H:%M:%S'
		time_now = datetime.datetime.now()
		epoch = int(time.mktime(time.strptime(
                    str(time_now).partition('.')[0].replace('-', '.'), pattern)))

		cursor = db.cursor()
		cursor.execute(f"SELECT member_id, wallet, last_rob FROM user WHERE member_id = {ctx.author.id}")
		result_robber = cursor.fetchone()

		if result_robber is None:
			return await ctx.send("`Please create an account first.`")

		cursor.execute(f"SELECT member_id, wallet, last_robbed FROM user WHERE member_id = {user_to_rob.id}")
		result_robbed = cursor.fetchone()

		if result_robbed is None:
			return await ctx.send("`The person you are trying to rob does not have an account.`")
		
		random_rob = random.randint(1, 6)

		if result_robber[2] is not None and result_robbed[2] is None:
			if result_robbed[1] > 800 and epoch - result_robber[2] >= 28800:
				if random_rob != 1 or random_rob != 6:
					loot = random.randint(100, 1000)
					sql = (f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
					val = (result_robber[1] + loot, epoch)	
					sql_r = (f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
					val_r = (result_robbed[1] - loot, epoch)
					cursor.execute(sql, val)
					cursor.execute(sql_r, val_r)
					db.commit()
					cursor.close()
				elif random_rob == 1:
					await ctx.send(f"`You were unable to rob {user_to_rob.name}`")
				elif random_rob == 6:
					loot = random.randint(100, result_robber[1])
					sql = (f"UPDATE user SET wallet = ?, last_rob = ? WHERE member_id = {ctx.author.id}")
					val = (result_robber[1] - loot, epoch)
					sql_r = (f"UPDATE user SET wallet = ?, last_robbed = ? WHERE member_id = {user_to_rob.id}")
					val_r = (result_robbed[1] + loot, epoch)
					cursor.execute(sql, val)
					cursor.execute(sql_r, val_r)
					db.commit()
					cursor.close()
			elif epoch - result_robber[2] < 28800:
				await ctx.send((f"`You can only rob once every 8 hours.`"))

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
			elif epoch - result_robbed[2] < 43200:
				await ctx.send(f"`This user was robbed in last the last 12 hours, give them a break.`")
				
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

		elif (result_robbed[2] is not None) and (result_robber[2] is not None):
			if ((result_robbed[1] > 800) and (epoch - result_robbed[2] >= 43200) and( epoch - result_robber[2] >= 28800)):
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
					await ctx.send((f"`You can only rob once every 8 hours.`"))
				elif epoch - result_robbed[2] < 43200:
					await ctx.send(f"`{user_to_rob.name} has been robbed in the last 12 hours. Please give them a break.`")

def setup(bot):
	bot.add_cog(Economy(bot))

