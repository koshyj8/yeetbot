from discord.ext import commands
from discord.ext.commands.converter import MemberConverter

import sqlite3
import random

def add_money(user:MemberConverter, amount:int):
	#Do stuff
	return


class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def createaccount(self, ctx):
		user = ctx.author
		db = sqlite3.connect(r'C:\Users\HP\Desktop\yeetbot\cogs\db\eco.sqlite', timeout=3)
		cursor = db.cursor()
		cursor.execute(f"SELECT member_id,server_id FROM main WHERE member_id = {ctx.message.author.id} WHERE ctx.author_d = {ctx.guild.id}")
		result = cursor.fetchone()
		if result is None:
			sql = ("INSERT INTO main(member_id,money, server_id) VALUES(?,?,?)")
			val = (ctx.message.author.id, 500, ctx.guild.id)
			cursor.execute(sql, val)
			db.commit()
			cursor.close()


def setup(bot):
	bot.add_cog(Economy(bot))
