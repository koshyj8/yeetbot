import asyncio
import random
import sqlite3
from random import randint, shuffle
from typing import Dict, List, Tuple, Union
import collections
import akinator
import discord
from aiotrivia import AiotriviaException, TriviaClient
from akinator.async_aki import Akinator
from core.utils.gamefuncs import *
from discord.ext import commands
from discord.ext.commands import BucketType, MemberConverter
from PIL import *

emojis_c = ['✅', '❌', '🤷', '👍', '👎', '⏮', '🛑']
emojis_w = ['✅', '❌']

with open(r"core\utils\WORD.LST", "r") as f:
	words = [word.strip() for word in f.readlines() if len(word.strip()) == 5]

aki = Akinator()

class Game(commands.Cog):
	"""GAME COMMANDS"""
	def __init__(self, bot):
		self.bot = bot
		self.trivia = TriviaClient()

	def check(self, word, guess):
		# Check if valid guess
		if guess == "quit":
			return True, "quit"
		if len(guess) != 5:
			return False, "Guess must be 5 characters."
		elif guess not in self.wordlist:
			return False, "Guess not in word list."

		# Get to use reacts
		response = ""
		for i in range(len(guess)):
			if guess[i] == word[i]:
				response += guess[i].upper()
			elif guess[i] in word:
				response += guess[i].lower()
			else:
				response += '\\'
		return True,

	@commands.command(name='2048')
	async def twenty(self, ctx):
		"""Play 2048 game"""
		await tplay(ctx, self.bot)

	@commands.command(name='minesweeper')
	async def minesweeper(self, ctx, columns=None, rows=None, bombs=None):
		"""Play Minesweeper"""
		await mplay(ctx, columns, rows, bombs)

	@commands.command(name='akinator')
	@commands.max_concurrency(1, per=BucketType.default)
	async def guess(self, ctx, *, category=None):

		if category == None:
			category = 'people'

		await ctx.send('`✅(YES), ❌(NO), 🤷(MAYBE), 👍(PROBABLY), 👎(PROBABLY NOT), ⏮(BACK), 🛑(END)`')

		def check_c(reaction, user):
			return user == ctx.author and str(
				reaction.emoji) in emojis_c and reaction.message.content == q

		def check_w(reaction, user):
			return user == ctx.author and str(reaction.emoji) in emojis_w

		if category == 'people':
			q = await aki.start_game(child_mode=False)
		elif category == 'objects' or category == 'animals':
			q = await aki.start_game(language=f'en_{category}',
									 child_mode=False)
			embed_question = discord.Embed(
				title='Please wait until all the reactions are added, otherwise you will have to unreact, then re-react.',
				color=discord.Color.random())
			await ctx.reply(embed=embed_question, allowed_mentions=discord.AllowedMentions(replied_user=False))

		else:
			await ctx.send('`The categories are : people , animals , objects`')

		while aki.progression <= 85:
			message = await ctx.reply(q, allowed_mentions=discord.AllowedMentions(replied_user=False))

			for m in emojis_c:
				await message.add_reaction(m)

			try:
				symbol, username = await self.bot.wait_for('reaction_add',
														   timeout=45.0,
														   check=check_c)
			except asyncio.TimeoutError:
				embed_game_ended = discord.Embed(
					title='`Time Out!`',
					color=0xFF0000)
				await ctx.reply(embed=embed_game_ended, allowed_mentions=discord.AllowedMentions(replied_user=False))
				return

			if str(symbol) == emojis_c[0]:
				a = 'y'
			elif str(symbol) == emojis_c[1]:
				a = 'n'
			elif str(symbol) == emojis_c[2]:
				a = 'idk'
			elif str(symbol) == emojis_c[3]:
				a = 'p'
			elif str(symbol) == emojis_c[4]:
				a = 'pn'
			elif str(symbol) == emojis_c[5]:
				a = 'b'
			elif str(symbol) == emojis_c[6]:
				embed_game_end = discord.Embed(
					title='lmao what a loser',
					color=discord.Color.random())
				await ctx.reply(embed=embed_game_end, allowed_mentions=discord.AllowedMentions(replied_user=False))
				return

			if a == "b":
				try:
					q = await aki.back()
				except akinator.CantGoBackAnyFurther:
					pass
			else:
				q = await aki.answer(a)

		await aki.win()

		wm = await ctx.reply(
			embed=w(aki.first_guess['name'], aki.first_guess['description'],
					aki.first_guess['absolute_picture_path']), allowed_mentions=discord.AllowedMentions(replied_user=False))

		for e in emojis_w:
			await wm.add_reaction(e)

		try:
			s, u = await self.bot.wait_for('reaction_add',
										   timeout=30.0,
										   check=check_w)
		except asyncio.TimeoutError:
			for times in aki.guesses:
				d_loss = d_loss + times['name'] + '\n'
			t_loss = 'Here is a list of all the people I had in mind :'
			embed_loss = discord.Embed(title=t_loss,
									   description=d_loss,
									   color=0xFF0000)
			await ctx.reply(embed=embed_loss, allowed_mentions=discord.AllowedMentions(replied_user=False))
			return

		if str(s) == emojis_w[0]:
			embed_win = discord.Embed(
				title='Great, guessed right one more time!', color=0x00FF00)
			await ctx.reply(embed=embed_win, allowed_mentions=discord.AllowedMentions(replied_user=False))
		elif str(s) == emojis_w[1]:
			for times in aki.guesses:
				desc_loss = desc_loss + times['name'] + '\n'
			title_loss = 'No problem, I will win next time! But here is a list of all the people I had in mind :'
			embed_loss = discord.Embed(title=title_loss,
									   description=desc_loss,
									   color=0xFF0000)
			await ctx.reply(embed=embed_loss, allowed_mentions=discord.AllowedMentions(replied_user=False))

	@commands.command()
	@commands.cooldown(3, 300, type=BucketType.user)
	async def trivia(self, ctx, difficulty=None):
		'''Trivia using the Open Trivia Database'''
		ez = ['easy', 'medium', 'hard']

		try:
			if difficulty == None:
				question1 = await self.trivia.get_random_question(random.choice(ez))
			else:
				question1 = await self.trivia.get_random_question(difficulty.lower())
			question = question1
		except AiotriviaException as error:
			return await ctx.send(f"\n`Difficulty Levels:`\n`Easy - 1 Point`\n`Medium - 2 Points`\n`Hard - 3 Points`")

		answers = question.responses
		random.shuffle(answers)

		final_answers = '\n'.join(
			[f"{index}. {value}" for index, value in enumerate(answers, 1)])
		diffic = question.difficulty
		message = await ctx.reply(f"``{question.question}``\n`{final_answers}`\n`{question.type.capitalize()}` `{question.category}`", allowed_mentions=discord.AllowedMentions(replied_user=False))
		answer = answers.index(question.answer)+1
		await self.trivia.close()

		try:
			while True:
				msg = await self.bot.wait_for('message', timeout=15, check=lambda m: m.author == ctx.message.author)
				if str(answer) == msg.content:
					db = sqlite3.connect(
						r'C:\Users\HP\Desktop\yeetbot\cogs\db\trivia.sqlite', timeout=3)
					if diffic == 'easy':
						point = 1
					elif diffic == 'medium':
						point = 2
					elif diffic == 'hard':
						point = 3
					cursor = db.cursor()
					cursor.execute(
						f"SELECT member_id,score FROM main WHERE member_id = {ctx.message.author.id}")
					result = cursor.fetchone()
					if result is None:
						sql = ("INSERT INTO main(member_id,score) VALUES(?,?)")
						val = (ctx.message.author.id, 1)
						cursor.execute(sql, val)
						db.commit()
						cursor.close()
					else:
						cursor.execute(
							f"SELECT member_id,score FROM main WHERE member_id ='{ctx.message.author.id}'")
						result1 = cursor.fetchone()
						score = int(result1[1])
						sql = ("UPDATE main SET score = ? WHERE member_id = ?")
						val = (int(score + point), ctx.message.author.id)
						cursor.execute(sql, val)
						db.commit()
						cursor.close()
						db.close()

					return await ctx.send(f"`{question.answer}` `is correct! wow ur so proo` ")

				else:
					return await ctx.send(f"`haha noob. The correct answer is:` `{question.answer}`")

		except asyncio.TimeoutError:
			await ctx.send(f"`Time ran out!` `{question.answer}` `is the corect answer`")

	@trivia.error
	async def trivia_error(self, ctx, error):
		if isinstance(error, commands.CommandOnCooldown):
			em = discord.Embed(title=f"Command on Cooldown!",
							   description=f"Try again in {error.retry_after:.2f}s.", color=discord.Color.random())
			await ctx.send(embed=em)

	@commands.command()
	async def scramble(self, ctx):
		'''Unscramble a word'''
		word = random.choice(words)
		l = list(word)
		scrambled = shuffle(l)
		y = ''.join(l)
		await ctx.reply(f"`Unscramble The Word : {y}`", allowed_mentions=discord.AllowedMentions(replied_user=False))
		msg = await self.bot.wait_for('message', timeout=15, check=lambda m: m.author == ctx.message.author)

		if msg.content == word:
			await msg.reply('`That was Correct!`', allowed_mentions=discord.AllowedMentions(replied_user=False))
		else:
			await msg.reply(f"`that was wrong, the correct word was : {word}`", allowed_mentions=discord.AllowedMentions(replied_user=False))

	@commands.command()
	async def triviaboard(self, ctx):
		db = sqlite3.connect(
			r'C:\Users\HP\Desktop\yeetbot\cogs\db\trivia.sqlite', timeout=3)
		cursor = db.cursor()
		cursor.execute(f"SELECT member_id,score FROM main ORDER BY score DESC")
		embed = discord.Embed(title='Trivia Leaderboard',
							  color=discord.Color.random())
		for i, pos in enumerate(cursor, start=1):
			member_id, score = pos

			if i == 1:
				i = "🥇"
			elif i == 2:
				i = '🥈'
			elif i == 3:
				i = '🥉'

			member = self.bot.get_user(member_id)
			embed.add_field(name=f'{i}.{member}',
							value=f'{score} Points', inline=False)

		await ctx.send(embed=embed)

	async def make_game_square(self, inserted: Dict[str, Tuple[int]], columns: int, rows: int, player_x: int, player_y: int, update: bool = False) -> str:
		""" Makes a game square with emojis. """

		emoji = '\u2B1B'
		# emoji = ':black_large_square:'

		simple_square = [[emoji for __ in range(columns)] for _ in range(rows)]
		# pprint(square)
		square = await self.make_square_border(simple_square, emoji, player_x, player_y)
		square, new_inserted = await self.put_objects(square, inserted, player_x, player_y, columns, rows, update)
		return square, new_inserted

	async def make_square_border(self, square: List[List[str]], emoji: str, player_x: int, player_y: int) -> List[List[str]]:
		""" Makes a border for the given square. """

		blue = ':blue_square:'

		new_list = []
		for i, row in enumerate(square):
			# print(i, row.replace())
			if i == 0 or i == len(square) - 1:
				new_row = []
				for column in row:
					column = blue
					new_row.append(column)
					# square[i].replace(emoji, blue)
				new_list.append(new_row)
			else:
				new_row = row
				new_row[0] = blue
				new_row[-1] = blue
				new_list.append(new_row)

		return new_list

	async def put_objects(self, square: List[List[str]], inserted: Dict[str, Tuple[int]], player_x: int, player_y: int, columns: int, rows: int, update: bool) -> List[List[str]]:
		""" Puts all objects into the game square field.
		:param square: The game square field. """

		# List of inserted items

		# Puts player
		player = '🐸'
		x = player_x
		y = player_y
		inserted['player'] = (x, y, player)

		if update:
			# Puts item
			square, item_tuple = await self.insert_item(square, columns, rows, inserted)
			inserted['item'] = item_tuple

			# Puts destiny
			square, destiny_tuple = await self.insert_destiny(square, columns, rows, inserted)
			inserted['destiny'] = destiny_tuple

		for values in inserted.values():
			x, y, emoji = values
			square[y][x] = emoji

		return square, inserted

	async def insert_item(self, square: List[List[str]], columns, rows, inserted: Dict[str, Tuple[int]]) -> Dict[str, Tuple[int]]:
		""""""

		item = '💎'

		while True:
			rand_x = randint(2, columns-3)
			rand_y = randint(2, rows-3)
			if (rand_x, rand_y) not in inserted.values():
				square[rand_y][rand_x] = item
				return square, (rand_x, rand_y, item)

	async def insert_destiny(self, square: List[List[str]], columns, rows, inserted: Dict[str, Tuple[int]]) -> Dict[str, Tuple[int]]:
		""""""

		destiny = '👸'

		while True:
			rand_x = randint(1, columns-2)
			rand_y = randint(1, rows-2)
			if (rand_x, rand_y) not in inserted.values():
				square[rand_y][rand_x] = destiny
				return square, (rand_x, rand_y, destiny)

	async def check_player_collision(self, inserted: Dict[str, List[int]], x: int, y: int, xadd: int, yadd: int, emj: str, columns: int, rows: int) -> Dict[str, List[Union[int, bool]]]:
		""" Checks collision of the player with items and the destinies.
		:param inserted: The objects inserted into the canvas.
		:param xadd: The addition to apply to the X axis, in case of collision.
		:param yadd: The addition to apply to the Y axis, in case of collision."""

		# player = inserted['player']
		moved = False
		gg = False

		item_x, item_y, item_emj = inserted['item']
		destiny_x, destiny_y, _ = inserted['destiny']

		if (x, y) == (item_x, item_y):

			if emj == '⬅️':
				if item_x - 1 > 0:

					inserted['item'] = (item_x+xadd, item_y+yadd, item_emj)
					moved = True
				else:
					moved = None

			elif emj == '➡️':
				if item_x + 1 < columns - 1:

					inserted['item'] = (item_x+xadd, item_y+yadd, item_emj)
					moved = True
				else:
					moved = None

			elif emj == '⬇️':
				if item_y + 1 < rows - 1:

					inserted['item'] = (item_x+xadd, item_y+yadd, item_emj)
					moved = True
				else:
					moved = None

			elif emj == '⬆️':
				if item_y - 1 > 0:

					inserted['item'] = (item_x+xadd, item_y+yadd, item_emj)
					moved = True
				else:
					moved = None
		elif (x, y) == (destiny_x, destiny_y):
			moved = None

		if moved and (item_x+xadd, item_y+yadd) == (destiny_x, destiny_y):
			moved = True
			gg = True

		return inserted, moved, gg

	async def remove_message_reaction(self, msg, member: discord.Member) -> None:
		""" Removes arrow reactions from a given message:
		:param msg: The message from which you want to remove the reactions. """

		await msg.remove_reaction('⬅️', self.client.user)
		await msg.remove_reaction('➡️', self.client.user)
		await msg.remove_reaction('⬇️', self.client.user)
		await msg.remove_reaction('⬆️', self.client.user)
		await msg.remove_reaction('🏳️', self.client.user)
		await msg.remove_reaction('⬅️', member)
		await msg.remove_reaction('➡️', member)
		await msg.remove_reaction('⬇️', member)
		await msg.remove_reaction('⬆️', member)
		await msg.remove_reaction('🏳️', member)

	@commands.command()
	async def frog(self, ctx) -> None:
		instructions = await ctx.send('`Get the diamond to the princess. (If the diamond is stuck to the wall, you lose. Use the white flag reaction to surrender)`')
		member = ctx.author

		embed = discord.Embed(
			title="frog.io",
			color=discord.Color.blue(),
			timestamp=ctx.message.created_at
		)

		columns, rows = 13, 9
		x, y = 6, 4
		gg = False
		inserted: Dict[str, Tuple[int]] = {'player': (x, y)}
		square, inserted = await self.make_game_square(inserted=inserted, columns=columns, rows=rows, player_x=x, player_y=y, update=True)

		msg = await ctx.send(embed=discord.Embed(title="Starting frog.io"))
		await asyncio.sleep(0.5)
		await msg.add_reaction('⬅️')
		await msg.add_reaction('➡️')
		await msg.add_reaction('⬇️')
		await msg.add_reaction('⬆️')
		await msg.add_reaction('🏳️')

		while True:

			square = '\n'.join(map(lambda r: ''.join(r), square))
			embed.description = square
			await msg.edit(embed=embed)
			if gg:
				embed.title = "frog.io"
				embed.color = discord.Color.green()
				await msg.edit(content="You Win!", embed=embed)
				self.bot.get_command('start').reset_cooldown(ctx)
				return await self.remove_message_reaction(msg, ctx.author)

			try:
				r, u = await self.bot.wait_for('reaction_add', timeout=60,
											   check=lambda r, u: u.id == member.id and r.message.id == msg.id and str(
												   r.emoji) in ['⬅️', '➡️', '⬇️', '⬆️', '🏳️']
											   )
			except asyncio.TimeoutError:
				await self.remove_message_reaction(msg, ctx.author)
				embed.title += ' (Timeout)'
				embed.color = discord.Color.red()
				self.bot.get_command('start').reset_cooldown(ctx)
				return await msg.edit(embed=embed)
			else:
				emj = str(r.emoji)

				if emj == '⬅️':
					await msg.remove_reaction(r, u)
					if x - 1 > 0:
						inserted, moved, gg = await self.check_player_collision(inserted, x-1, y, -1, 0, emj, columns, rows)
						if moved is not None:
							x -= 1

				elif emj == '➡️':
					await msg.remove_reaction(r, u)
					if x + 1 < columns - 1:
						inserted, moved, gg = await self.check_player_collision(inserted, x+1, y, 1, 0, emj, columns, rows)
						if moved is not None:
							x += 1

				elif emj == '⬇️':
					await msg.remove_reaction(r, u)
					if y + 1 < rows - 1:
						inserted, moved, gg = await self.check_player_collision(inserted, x, y+1, 0, 1, emj, columns, rows)
						if moved is not None:
							y += 1

				elif emj == '⬆️':
					await msg.remove_reaction(r, u)
					if y - 1 > 0:
						inserted, moved, gg = await self.check_player_collision(inserted, x, y-1, 0, -1, emj, columns, rows)
						if moved is not None:
							y -= 1
				elif emj == '🏳️':
					embed.color = discord.Color.orange()
					await msg.edit(content="You lose!", embed=embed)
					self.bot.get_command('start').reset_cooldown(ctx)
					return await self.remove_message_reaction(msg, ctx.author)

				square, inserted = await self.make_game_square(inserted=inserted, columns=columns, rows=rows, player_x=x, player_y=y)

	@commands.command(name="fight")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def fight(self, ctx, member: MemberConverter):

		if member.bot or member == ctx.author:
			return await ctx.send("`You can only fight another member.`")

		users = [ctx.author, member]

		user1 = random.choice(users)
		user2 = ctx.author if user1 == member else member

		user1_hp = 100
		user2_hp = 100

		fails_user1 = 0
		fails_user2 = 0

		x = 2

		while True:
			if user1_hp <= 0 or user2_hp <= 0:
				winner = user1 if user2_hp <= 0 else user2
				loser = user2 if winner == user1 else user1
				winner_hp = user1_hp if user2_hp <= 0 else user2_hp
				db = sqlite3.connect(
					r'C:\Users\HP\Desktop\yeetbot\cogs\db\fight.sqlite', timeout=3)
				cursor = db.cursor()
				cursor.execute(
					f"SELECT member_id, score FROM main WHERE member_id = {winner.id}")
				result = cursor.fetchone()
				point = 1
				if result is None:
					sql = ("INSERT INTO main(member_id,score) VALUES(?,?)")
					val = (winner.id, 1)
					cursor.execute(sql, val)
					db.commit()
					cursor.close()
				else:

					cursor.execute(
						f"SELECT member_id,score FROM main WHERE member_id ='{winner.id}'")
					result1 = cursor.fetchone()
					score = int(result1[1])
					sql = ("UPDATE main SET score = ? WHERE member_id = ?")
					val = (int(score + point), winner.id)
					cursor.execute(sql, val)
					db.commit()
					cursor.close()
					db.close()

				await ctx.send(
					random.choice(
						[
							f"`Holy Fu-! {winner.name} just destroyed {loser.name}, winning with just {winner_hp} HP left!`",
							f"`Well Played! {winner.name} pulled a thanos snap on {loser.name}, winning with {winner_hp} HP left.`",
							f"`That was amazing! {winner.name} sends {loser.name} home crying... with only {winner_hp} HP left!`",
							f"`Holy cow! {winner.name} won from {loser.name} with {winner_hp} HP left. {loser.name} must be so embarassed.`",
						]
					)
				)
				return

			alpha = user1 if x % 2 == 0 else user2
			beta = user2 if alpha == user1 else user1
			await ctx.send(
				f"{alpha.mention}, what do you want to do? `punch`, `kick`, `slap` or `end`?\nType out ur move, word for word."
			)

			def check(m):
				if alpha == user1:
					return m.author == user1 and m.channel == ctx.channel
				else:
					return m.author == user2 and m.channel == ctx.channel

			try:
				msg = await self.bot.wait_for("message", timeout=15.0, check=check)
			except asyncio.TimeoutError:
				await ctx.send(
					f"`{alpha.name} has some shit reaction time. What a noob. {beta.name} wins!`"
				)
				return

			if msg.content.lower() == "punch":
				damage = random.choice(
					[
						random.randint(20, 60),
						random.randint(0, 50),
						random.randint(30, 70),
						random.randint(0, 40),
						random.randint(10, 30),
						random.randint(5, 10),
					]
				)

				if alpha == user1:
					user2_hp -= damage
					hpover = 0 if user2_hp < 0 else user2_hp
				else:
					user1_hp -= damage
					hpover = 0 if user1_hp < 0 else user1_hp

				randommsg = random.choice(
					[
						f"`{alpha.name} deals {damage} damage with a staggering punch.\n{beta.name} is left with {hpover} HP`",
						f"`{alpha.name} lands a superman punch on {beta.name} dealing {damage} damage!\n{beta.name} is left over with {hpover} HP!`",
						f"`{alpha.name} lands a heavy punch on {beta.name} dealing {damage} damage!\n{beta.name} is left over with {hpover} HP!`",
					]
				)
				await ctx.send(f"{randommsg}")

			elif msg.content.lower() == "kick":
				damage = random.choice(
					[
						random.randint(30, 45),
						random.randint(30, 60),
						random.randint(-50, -1),
						random.randint(-40, -1),
					]
				)
				if damage > 0:

					if alpha == user1:
						user2_hp -= damage
						hpover = 0 if user2_hp < 0 else user2_hp
					else:
						user1_hp -= damage
						hpover = 0 if user1_hp < 0 else user1_hp

					await ctx.send(
						random.choice(
							[
								f"`{alpha.name} boots {beta.name} and deals {damage} damage\n{beta.name} is left over with {hpover} HP`",
								f"`{alpha.name} lands a hard front kick on {beta.name}, dealing {damage} damage.\n{beta.name} is left over with {hpover} HP`",
							]
						)
					)
				elif damage < 0:

					if alpha == user1:
						user1_hp += damage
						hpover = 0 if user1_hp < 0 else user1_hp
					else:
						user2_hp += damage
						hpover = 0 if user2_hp < 0 else user2_hp

					await ctx.send(
						random.choice(
							[
								f"`{alpha.name} slipped while trying to kick their opponent, dealing {-damage} damage to themselves.`",
								f"`{alpha.name} tried to kick {beta.name} but flipped out! They took {-damage} damage!`",
							]
						)
					)

			elif msg.content.lower() == "slap":
				damage = random.choice(
					[
						random.randint(20, 60),
						random.randint(0, 50),
						random.randint(30, 70),
						random.randint(0, 40),
						random.randint(10, 30),
						random.randint(5, 10),
					]
				)

				if alpha == user1:
					user2_hp -= damage
					hpover = 0 if user2_hp < 0 else user2_hp
				else:
					user1_hp -= damage
					hpover = 0 if user1_hp < 0 else user1_hp

				await ctx.send(
					f"`{alpha.name} slaps their opponent, and deals {damage} damage.\n{beta.name} is left over with {hpover} HP`"
				)

			elif msg.content.lower() == "end":
				await ctx.send(f"`{alpha.name} ended the game. What a nub.`")
				return

			elif (
				msg.content.lower() != "kick"
				and msg.content.lower() != "slap"
				and msg.content.lower() != "punch"
				and msg.content.lower() != "end"
			):
				if fails_user1 >= 1 or fails_user2 >= 1:
					return await ctx.send(
						"`How did u manage to make so many invalid choices???`"
					)
				if alpha == user1:
					fails_user1 += 1
				else:
					fails_user2 += 1
				await ctx.send("`That is not a valid choice!`")
				x -= 1

			x += 1

	@commands.command(name='wordle')
	async def wordle(self, ctx):
		with open(r"core\utils\WORD.LST", "r") as f:
			words = [word.strip()
					for word in f.readlines() if len(word.strip()) == 5]
		while len(words) > 1:
			await ctx.send(f'{ctx.message.author.mention} - Try ``{(guess := random.choice(words))}``. (Send a 5 digit response back. 0 is gray, 1 is yellow, and 2 is green.)')

			def check(m):
				return ctx.channel == m.channel and ctx.author == m.author
			try:
				msg = await self.bot.wait_for('message', check=check, timeout=40)
				message = msg.content
				if len(message) == 5 and message.isdigit():
					score = [int(char) for char in msg.content if char in "012"]
				else:
					await ctx.send("`Only send a 5 digit response.`")
			except:
				await ctx.send("`The command has timed-out. Please try again.`")
			words_ = []
			for word in words:
				pool = collections.Counter(
					c for c, sc in zip(word, score) if sc != 2)
				for w, g, sc in zip(word, guess, score):
					if ((sc == 2) != (w == g)) or (sc < 2 and bool(sc) != bool(pool[g])):
						break
					pool[g] -= sc == 1
				else:
					words_.append(word)  # No `break` was hit, so store the word.
			words = words_
		try:
			await ctx.send(f'{ctx.message.author.mention} - The word is ***{words[0]}***.')
		except IndexError:
			await ctx.send(f'{ctx.message.author.mention} - No words found. Good luck on this one!')


async def setup(bot):
    await bot.add_cog(Game(bot))
