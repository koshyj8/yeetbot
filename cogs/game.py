from typing import List
import asyncio
import akinator
from discord.ext import commands
from discord.ext.commands import BucketType
from typing import List, Union, Tuple, Dict
from discord.ext import commands
import random
from random import randint
import random
from discord.ext import commands
from discord.ext.commands import MemberConverter
from discord import Embed
from time import time
import asyncio

import asyncio
import random
from copy import deepcopy as dc

from random import shuffle
from akinator.async_aki import Akinator
import discord
from discord.ext.commands.converter import MemberConverter

emojis_c = ['✅', '❌', '🤷', '👍', '👎', '⏮', '🛑']
emojis_w = ['✅', '❌']

from discord import Embed
import random
import os,sys
from aiotrivia import AiotriviaException, ResponseError, TriviaClient
import sqlite3
from akinator.async_aki import Akinator
import akinator

player1 = ""
player2 = ""
turn = ""
gameOver = True

aki = Akinator()


room_status = {1 : False, 2 : False, 3 : False, 4 : False, 5 : False}
rooms = {}

_party = []
playerPoints = {}
confirm = False
users = {}

HangmanInProgress = {}

words = ["a","ability","able","about","above","accept","according", "account", "across", "act", "action", "activity", "actually", "add", "address", "administration", "admit", "adult", "affect", "after", "again", "against", "age", "agency", "agent", "ago", "agree", "agreement", "ahead", "air", "all", "allow", "almost", "alone", "along", "already", "also", "although", "always", "American", "among", "amount", "analysis", "and", "animal", "another", "answer", "any", "anyone", "anything", "appear", "apply", "approach", "area", "argue", "arm", "around", "arrive", "art", "article", "artist", "as", "ask", "assume", "at", "attack", "attention", "attorney", "audience", "author", "authority", "available", "avoid", "away", "baby", "back", "bad", "bag", "ball", "bank", "bar", "base", "be", "beat", "beautiful", "because", "become", "bed", "before", "begin", "behavior", "behind", "believe", "benefit", "best", "better", "between", "beyond", "big", "bill", "billion", "bit", "black", "blood", "blue", "board", "body", "book", "born", "both", "box", "boy", "break", "bring", "brother", "budget", "build", "building", "business", "but", "buy", "by", "call", "camera", "campaign", "can", "cancer", "candidate", "capital", "car", "card", "care", "career", "carry", "case", "catch", "cause", "cell", "center", "central", "century", "certain", "certainly", "chair", "challenge", "chance", "change", "character", "charge", "check", "child", "choice", "choose", "church", "citizen", "city", "civil", "claim", "class", "clear", "clearly", "close", "coach", "cold", "collection", "college", "color", "come", "commercial", "common", "community", "company", "compare", "computer", "concern", "condition", "conference", "Congress", "consider", "consumer", "contain", "continue", "control", "cost", "could", "country", "couple", "course", "court", "cover", "create", "crime", "cultural", "culture", "cup", "current", "customer", "cut", "dark", "data", "daughter", "day", "dead", "deal", "death", "debate", "decade", "decide", "decision", "deep", "defense", "degree", "Democrat", "democratic", "describe", "design", "despite", "detail", "determine", "develop", "development", "die", "difference", "different", "difficult", "dinner", "direction", "director", "discover", "discuss", "discussion", "disease", "do", "doctor", "dog", "door", "down", "draw", "dream", "drive", "drop", "drug", "during", "each", "early", "east", "easy", "eat", "economic", "economy", "edge", "education", "effect", "effort", "eight", "either", "election", "else", "employee", "end", "energy", "enjoy", "enough", "enter", "entire", "environment", "environmental", "especially", "establish", "even", "evening", "event", "ever", "every", "everybody", "everyone", "everything", "evidence", "exactly", "example", "executive", "exist", "expect", "experience", "expert", "explain", "eye", "face", "fact", "factor", "fail", "fall", "family", "far", "fast", "father", "fear", "federal", "feel", "feeling", "few", "field", "fight", "figure", "fill", "film", "final", "finally", "financial", "find", "fine", "finger", "finish", "fire", "firm", "first", "fish", "five", "floor", "fly", "focus", "follow", "food", "foot", "for", "force", "foreign", "forget", "form", "former", "forward", "four", "free", "friend", "from", "front", "full", "fund", "future", "game", "garden", "gas", "general", "generation", "get", "girl", "give", "glass", "go", "goal", "good", "government", "great", "green", "ground", "group", "grow", "growth", "guess", "gun", "guy", "hair", "half", "hand", "hang", "happen", "happy", "hard", "have", "he", "head", "health", "hear", "heart", "heat", "heavy", "help", "her", "here", "herself", "high", "him", "himself", "his", "history", "hit", "hold", "home", "hope", "hospital", "hot", "hotel", "hour", "house", "how", "however", "huge", "human", "hundred", "husband", "I", "idea", "identify", "if", "image", "imagine", "impact", "important", "improve", "in", "include", "including", "increase", "indeed", "indicate", "individual", "industry", "information", "inside", "instead", "institution", "interest", "interesting", "international", "interview", "into", "investment", "involve", "issue", "it", "item", "its", "itself", "job", "join", "just", "keep", "key", "kid", "kill", "kind", "kitchen", "know", "knowledge", "land", "language", "large", "last", "late", "later", "laugh", "law", "lawyer", "lay", "lead", "leader", "learn", "least", "leave", "left", "leg", "legal", "less", "let", "letter", "level", "lie", "life", "light", "like", "likely", "line", "list", "listen", "little", "live", "local", "long", "look", "lose", "loss", "lot", "love", "low", "machine", "magazine", "main", "maintain", "major", "majority", "make", "man", "manage", "management", "manager", "many", "market", "marriage", "material", "matter", "may", "maybe", "me", "mean", "measure", "media", "medical", "meet", "meeting", "member", "memory", "mention", "message", "method", "middle", "might", "military", "million", "mind", "minute", "miss", "mission", "model", "modern", "moment", "money", "month", "more", "morning", "most", "mother", "mouth", "move", "movement", "movie", "Mr", "Mrs", "much", "music", "must", "my", "myself", "name", "nation", "national", "natural", "nature", "near", "nearly", "necessary", "need", "network", "never", "new", "news", "newspaper", "next", "nice", "night", "no", "none", "nor", "north", "not", "note", "nothing", "notice", "now", "n't", "number", "occur", "of", "off", "offer", "office", "officer", "official", "often", "oh", "oil", "ok", "old", "on", "once", "one", "only", "onto", "open", "operation", "opportunity", "option", "or", "order", "organization", "other", "others", "our", "out", "outside", "over", "own", "owner", "page", "pain", "painting", "paper", "parent", "part", "participant", "particular", "particularly", "partner", "party", "pass", "past", "patient", "pattern", "pay", "peace", "people", "per", "perform", "performance", "perhaps", "period", "person", "personal", "phone", "physical", "pick", "picture", "piece", "place", "plan", "plant", "play", "player", "PM", "point", "police", "policy", "political", "politics", "poor", "popular", "population", "position", "positive", "possible", "power", "practice", "prepare", "present", "president", "pressure", "pretty", "prevent", "price", "private", "probably", "problem", "process", "produce", "product", "production", "professional", "professor", "program", "project", "property", "protect", "prove", "provide", "public", "pull", "purpose", "push", "put", "quality", "question", "quickly", "quite", "race", "radio", "raise", "range", "rate", "rather", "reach", "read", "ready", "real", "reality", "realize", "really", "reason", "receive", "recent", "recently", "recognize", "record", "red", "reduce", "reflect", "region", "relate", "relationship", "religious", "remain", "remember", "remove", "report", "represent", "Republican", "require", "research", "resource", "respond", "response", "responsibility", "rest", "result", "return", "reveal", "rich", "right", "rise", "risk", "road", "rock", "role", "room", "rule", "run", "safe", "same", "save", "say", "scene", "school", "science", "scientist", "score", "sea", "season", "seat", "second", "section", "security", "see", "seek", "seem", "sell", "send", "senior", "sense", "series", "serious", "serve", "service", "set", "seven", "several", "sex", "sexual", "shake", "share", "she", "shoot", "short", "shot", "should", "shoulder", "show", "side", "sign", "significant", "similar", "simple", "simply", "since", "sing", "single", "sister", "sit", "site", "situation", "six", "size", "skill", "skin", "small", "smile", "so", "social", "society", "soldier", "some", "somebody", "someone", "something", "sometimes", "son", "song", "soon", "sort", "sound", "source", "south", "southern", "space", "speak", "special", "specific", "speech", "spend", "sport", "spring", "staff", "stage", "stand", "standard", "star", "start", "state", "statement", "station", "stay", "step", "still", "stock", "stop", "store", "story", "strategy", "street", "strong", "structure", "student", "study", "stuff", "style", "subject", "success", "successful", "such", "suddenly", "suffer", "suggest", "summer", "support", "sure", "surface", "system", "table", "take", "talk", "task", "tax", "teach", "teacher", "team", "technology", "television", "tell", "ten", "tend", "term", "test", "than", "thank", "that", "the", "their", "them", "themselves", "then", "theory", "there", "these", "they", "thing", "think", "third", "this", "those", "though", "thought", "thousand", "threat", "three", "through", "throughout", "throw", "thus", "time", "to", "today", "together", "tonight", "too", "top", "total", "tough", "toward", "town", "trade", "traditional", "training", "travel", "treat", "treatment", "tree", "trial", "trip", "trouble", "true", "truth", "try", "turn", "TV", "two", "type", "under", "understand", "unit", "until", "up", "upon", "us", "use", "usually", "value", "various", "very", "victim", "view", "violence", "visit", "voice", "vote", "wait", "walk", "wall", "want", "war", "watch", "water", "way", "we", "weapon", "wear", "week", "weight", "well", "west", "western", "what", "whatever", "when", "where", "whether", "which", "while", "white", "who", "whole", "whom", "whose","why","wide","wife","will","win","wind","window","wish","with","within","without","woman","wonder","word","work","worker","world","worry","would","write","writer","wrong","yard","yeah","year","yes","yet","you","young","your","yourself"]

def w(name, desc, picture):
	embed_win = discord.Embed(title=f"It's {name} ({desc})! Was I correct?",
							  colour=0x00FF00)
	embed_win.set_image(url=picture)
	return embed_win

errortxt = ('`Those are wrong arguments`\n',
			'`Use it as !minesweeper <col> <row> <bombs>`\n',
			'`For random columns, rows, and bombs use only !minesweeper`')
errortxt = ''.join(errortxt)
board = []

winningConditions = [
	[0, 1, 2],
	[3, 4, 5],
	[6, 7, 8],
	[0, 3, 6],
	[1, 4, 7],
	[2, 5, 8],
	[0, 4, 8],
	[2, 4, 6]]

def checkWinner(winningConditions, mark):
	global gameOver
	for condition in winningConditions:
		if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
			gameOver = True

async def mplay(ctx, columns=None, rows=None, bombs=None):
	if columns is None or rows is None and bombs is None:
		if columns is not None or rows is not None or bombs is not None:
			return await ctx.send(errortxt)
		else:
			columns = random.randint(4, 13)
			rows = random.randint(4, 13)
			bombs = columns * rows - 1
			bombs = bombs / 2.5
			bombs = round(random.randint(5, round(bombs)))
	try:
		columns = int(columns)
		rows = int(rows)
		bombs = int(bombs)
	except (ValueError, TypeError):
		return await ctx.send(errortxt)
	if columns > 13 or rows > 13:
		return await ctx.send('`The limit is 13 rows or columns, due to discord limits`')
	if columns < 1 or rows < 1 or bombs < 1:
		return await ctx.send('`Numbers cannot be negative`')
	if bombs + 1 > columns * rows:
		return await ctx.send('There are more bombs on your spaces')

	grid = [[0 for num in range(columns)] for num in range(rows)]

	loop_count = 0
	while loop_count < bombs:
		x = random.randint(0, columns - 1)
		y = random.randint(0, rows - 1)
		if grid[y][x] == 0:
			grid[y][x] = 'B'
			loop_count = loop_count + 1
		# It will loop again if a bomb is already selected at a random point
		if grid[y][x] == 'B':
			pass

	# The while loop will go though every point though our makeshift grid
	pos_x = 0
	pos_y = 0
	while pos_x * pos_y < columns * rows and pos_y < rows:
		# We need to predefine this for later
		adj_sum = 0
		# Checks the surrounding points of our "grid"
		for (adj_y, adj_x) in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
			# There will be index errors, we can just simply ignore them by using a try and exception block
			try:
				if grid[adj_y + pos_y][adj_x + pos_x] == 'B' and adj_y + pos_y > -1 and adj_x + pos_x > -1:
					# adj_sum will go up by 1 if a surrounding point has a bomb
					adj_sum = adj_sum + 1
			except Exception as error:
				pass
		# Since we don't want to change the Bomb variable into a number,
		# the point that the loop is in will only change if it isn't "B"
		if grid[pos_y][pos_x] != 'B':
			grid[pos_y][pos_x] = adj_sum
		# Increases the X values until it is more than the columns
		# If the while loop does not have "pos_y < rows" will index error
		if pos_x == columns - 1:
			pos_x = 0
			pos_y = pos_y + 1
		else:
			pos_x = pos_x + 1

	# Builds the string to be discord-ready
	string_builder = []
	for the_rows in grid:
		string_builder.append(''.join(map(str, the_rows)))
	string_builder = '\n'.join(string_builder)
	# Replaces the numbers and B for the respective emotes and spoiler tags
	string_builder = string_builder.replace('0', '||       ||')
	string_builder = string_builder.replace('1', '||:one:||')
	string_builder = string_builder.replace('2', '||:two:||')
	string_builder = string_builder.replace('3', '||:three:||')
	string_builder = string_builder.replace('4', '||:four:||')
	string_builder = string_builder.replace('5', '||:five:||')
	string_builder = string_builder.replace('6', '||:six:||')
	string_builder = string_builder.replace('7', '||:seven:||')
	string_builder = string_builder.replace('8', '||:eight:||')
	final = string_builder.replace('B', '||:bomb:||')

	percentage = columns * rows
	percentage = bombs / percentage
	percentage = 100 * percentage
	percentage = round(percentage, 2)



	embed = Embed(title='Minesweeper', color=discord.Color.random())
	embed.add_field(name='Columns:', value=columns, inline=True)
	embed.add_field(name='Rows:', value=rows, inline=True)
	embed.add_field(name='Total Spaces:', value=columns * rows, inline=True)
	embed.add_field(name='\U0001F4A3 Count:', value=bombs, inline=True)
	embed.add_field(name='\U0001F4A3 Percentage:',
					value=f'{percentage}%', inline=True)
	embed.add_field(name='Player:',
					value=ctx.author.display_name, inline=True)
	embed.add_field(name='Limit:',value='If your grid is between 81 - 169 tiles, hitting three bombs, kills you. If it is less, it only requires two bombs to lose',inline=True)
	await ctx.send(content=f'\U0000FEFF\n{final}', embed=embed)

async def tplay(ctx, bot):
	"""Starts a 2048 game inside of discord."""
	board = [
		["_", "_", "_", "_"],
		["_", "_", "_", "_"],
		["_", "_", "_", "_"],
		["_", "_", "_", 2],]
	score = 0
	total = 0
	await ctx.send("`Starting a game of 2048`\n`If a reaction is not received every 5 minutes, the game will time out.`")
	message = await ctx.send(f"`Score: {score}`\n```{print_board(board)}```")
	await message.add_reaction("\u2B05")
	await message.add_reaction("\u27A1")
	await message.add_reaction("\u2B06")
	await message.add_reaction("\u2B07")
	await message.add_reaction("\u274C")

	def check(reaction, user):
		return (
			(user.id == ctx.author.id)
			and (str(reaction.emoji) in ["\u2B06", "\u2B07", "\u2B05", "\u27A1", "\u274C"])
			and (reaction.message.id == message.id)
		)

	while True:
		try:
			reaction, user = await bot.wait_for(
				"reaction_add", check=check, timeout=300.0
			)
		except asyncio.TimeoutError:
			await ctx.send("`time ran out`")
			await message.delete()
			return
		else:
			try:
				await message.remove_reaction(str(reaction.emoji), ctx.author)
			except discord.errors.Forbidden:
				pass
			if str(reaction.emoji) == "\u2B06":
				msg, nb, total = execute_move("up", board)
			elif str(reaction.emoji) == "\u2B07":
				msg, nb, total = execute_move("down", board)
			elif str(reaction.emoji) == "\u2B05":
				msg, nb, total = execute_move("left", board)
			elif str(reaction.emoji) == "\u27A1":
				msg, nb, total = execute_move("right", board)
			elif str(reaction.emoji) == "\u274C":
				await ctx.send("`what a nub`")
				await message.delete()
				return
			score += total
			if msg == "Lost":
				await ctx.send(
					f"omg u suck {ctx.author.mention}.  you scored {score}!"
				)
				await message.delete()
				return
			board = nb
			await message.edit(content=f"Score: `{score}````{print_board(board)}```")

def print_board(board):
	col_width = max(len(str(word))
					for row in board for word in row) + 2  # padding
	whole_thing = ""
	for row in board:
		whole_thing += "".join(str(word).ljust(col_width) for word in row) + "\n"
	return whole_thing

def execute_move(move, pboard):
	board = dc(pboard)
	total = 0
	if move.lower() == "left":
		nb, total = check_left(board)
		for x in range(len(nb)):
			while nb[x][0] == "_" and (nb[x][1] != "_" or nb[x][2] != "_" or nb[x][3] != "_"):
				nb[x][0] = nb[x][1]
				nb[x][1] = nb[x][2]
				nb[x][2] = nb[x][3]
				nb[x][3] = "_"
			while nb[x][1] == "_" and (nb[x][2] != "_" or nb[x][3] != "_"):
				nb[x][1] = nb[x][2]
				nb[x][2] = nb[x][3]
				nb[x][3] = "_"
			while nb[x][2] == "_" and (nb[x][3] != "_"):
				nb[x][2] = nb[x][3]
				nb[x][3] = "_"
	if move.lower() == "right":
		nb, total = check_right(board)
		for x in range(len(nb)):
			while nb[x][3] == "_" and (nb[x][2] != "_" or nb[x][1] != "_" or nb[x][0] != "_"):
				nb[x][3] = nb[x][2]
				nb[x][2] = nb[x][1]
				nb[x][1] = nb[x][0]
				nb[x][0] = "_"
			while nb[x][2] == "_" and (nb[x][1] != "_" or nb[x][0] != "_"):
				nb[x][2] = nb[x][1]
				nb[x][1] = nb[x][0]
				nb[x][0] = "_"
			while nb[x][1] == "_" and (nb[x][0] != "_"):
				nb[x][1] = nb[x][0]
				nb[x][0] = "_"
	if move.lower() == "down":
		nb = columize(board)
		nb, total = check_down(nb)
		for x in range(len(nb)):
			while nb[x][0] == "_" and (nb[x][1] != "_" or nb[x][2] != "_" or nb[x][3] != "_"):
				nb[x][0] = nb[x][1]
				nb[x][1] = nb[x][2]
				nb[x][2] = nb[x][3]
				nb[x][3] = "_"
			while nb[x][1] == "_" and (nb[x][2] != "_" or nb[x][3] != "_"):
				nb[x][1] = nb[x][2]
				nb[x][2] = nb[x][3]
				nb[x][3] = "_"
			while nb[x][2] == "_" and (nb[x][3] != "_"):
				nb[x][2] = nb[x][3]
				nb[x][3] = "_"
		nb = rowize(nb)
	if move.lower() == "up":
		nb = columize(board)
		nb, total = check_up(nb)
		for x in range(len(nb)):
			while nb[x][3] == "_" and (nb[x][2] != "_" or nb[x][1] != "_" or nb[x][0] != "_"):
				nb[x][3] = nb[x][2]
				nb[x][2] = nb[x][1]
				nb[x][1] = nb[x][0]
				nb[x][0] = "_"
			while nb[x][2] == "_" and (nb[x][1] != "_" or nb[x][0] != "_"):
				nb[x][2] = nb[x][1]
				nb[x][1] = nb[x][0]
				nb[x][0] = "_"
			while nb[x][1] == "_" and (nb[x][0] != "_"):
				nb[x][1] = nb[x][0]
				nb[x][0] = "_"
		nb = rowize(nb)
	if (
		nb != pboard
	): 
		some_message, nb = add_number(nb)
	else:
		some_message = ""
	if some_message.startswith("Lost"):
		return "Lost", nb, total
	else:
		return "", nb, total

def add_number(board):
	try:
		row = random.randint(0, 3)
	except RecursionError:
		return "Lost", board
	if "_" in board[row]:
		number_of_zeroes = board[row].count("_")
		if number_of_zeroes == 1:
			column = board[row].index("_")
		else:
			column = random.randint(0, 3)
			while board[row][column] != "_":
				column = random.randint(0, 3)
	else:
		result, board = add_number(board)
		return result, board
	joining = random.randint(0, 100)
	if joining < 85:
		joining = 2
	else:
		joining = 4
	board[row][column] = joining
	return "", board

def columize(board):
	new_board = [[], [], [], []]
	# Make first column
	new_board[0].append(board[3][0])
	new_board[0].append(board[2][0])
	new_board[0].append(board[1][0])
	new_board[0].append(board[0][0])
	# Make second column
	new_board[1].append(board[3][1])
	new_board[1].append(board[2][1])
	new_board[1].append(board[1][1])
	new_board[1].append(board[0][1])
	# Make third column
	new_board[2].append(board[3][2])
	new_board[2].append(board[2][2])
	new_board[2].append(board[1][2])
	new_board[2].append(board[0][2])
	# Make fourth column
	new_board[3].append(board[3][3])
	new_board[3].append(board[2][3])
	new_board[3].append(board[1][3])
	new_board[3].append(board[0][3])
	board = new_board
	return board

def rowize(board):
	new_board = [[], [], [], []]
	# Make first row
	new_board[0].append(board[0][3])
	new_board[0].append(board[1][3])
	new_board[0].append(board[2][3])
	new_board[0].append(board[3][3])
	# Make second row
	new_board[1].append(board[0][2])
	new_board[1].append(board[1][2])
	new_board[1].append(board[2][2])
	new_board[1].append(board[3][2])
	# Make third row
	new_board[2].append(board[0][1])
	new_board[2].append(board[1][1])
	new_board[2].append(board[2][1])
	new_board[2].append(board[3][1])
	# Make fourth row
	new_board[3].append(board[0][0])
	new_board[3].append(board[1][0])
	new_board[3].append(board[2][0])
	new_board[3].append(board[3][0])
	board = new_board
	return board

def check_left(board):
	total = 0
	for x in range(len(board)):
		for y in range(len(board[x])):
			try:
				if board[x][y + 1] != "_":
					if board[x][y] == board[x][y + 1]:
						board[x][y] = board[x][y] + board[x][y + 1]
						total += board[x][y]
						board[x][y + 1] = "_"
				elif board[x][y + 2] != "_":
					if board[x][y] == board[x][y + 2]:
						board[x][y] = board[x][y] + board[x][y + 2]
						total += board[x][y]
						board[x][y + 2] = "_"
				elif board[x][y + 3] != "_":
					if board[x][y] == board[x][y + 3]:
						board[x][y] = board[x][y] + board[x][y + 3]
						total += board[x][y]
						board[x][y + 3] = "_"
			except IndexError:
				pass
	return board, total

def check_right(board):
	total = 0
	for x in range(len(board)):
		board[x].reverse()
		for y in range(len(board[x])):
			try:
				if board[x][y + 1] != "_":
					if board[x][y] == board[x][y + 1]:
						board[x][y] = board[x][y] + board[x][y + 1]
						total += board[x][y]
						board[x][y + 1] = "_"
				elif board[x][y + 2] != "_":
					if board[x][y] == board[x][y + 2]:
						board[x][y] = board[x][y] + board[x][y + 2]
						total += board[x][y]
						board[x][y + 2] = "_"
				elif board[x][y + 3] != "_":
					if board[x][y] == board[x][y + 3]:
						board[x][y] = board[x][y] + board[x][y + 3]
						total += board[x][y]
						board[x][y + 3] = "_"
			except IndexError:
				pass
		board[x].reverse()
	return board, total

def check_up(board):
	total = 0
	for x in range(len(board)):
		board[x].reverse()
		for y in range(len(board[x])):
			try:
				if board[x][y + 1] != "_":
					if board[x][y] == board[x][y + 1]:
						board[x][y] = board[x][y] + board[x][y + 1]
						total += board[x][y]
						board[x][y + 1] = "_"
				elif board[x][y + 2] != "_":
					if board[x][y] == board[x][y + 2]:
						board[x][y] = board[x][y] + board[x][y + 2]
						total += board[x][y]
						board[x][y + 2] = "_"
				elif board[x][y + 3] != "_":
					if board[x][y] == board[x][y + 3]:
						board[x][y] = board[x][y] + board[x][y + 3]
						total += board[x][y]
						board[x][y + 3] = "_"
			except IndexError:
				pass
		board[x].reverse()
	return board, total

def check_down(board):
	total = 0
	for x in range(len(board)):
		for y in range(len(board[x])):
			try:
				if board[x][y + 1] != "_":
					if board[x][y] == board[x][y + 1]:
						board[x][y] = board[x][y] + board[x][y + 1]
						total += board[x][y]
						board[x][y + 1] = "_"
				elif board[x][y + 2] != "_":
					if board[x][y] == board[x][y + 2]:
						board[x][y] = board[x][y] + board[x][y + 2]
						total += board[x][y]
						board[x][y + 2] = "_"
				elif board[x][y + 3] != "_":
					if board[x][y] == board[x][y + 3]:
						board[x][y] = board[x][y] + board[x][y + 3]
						total += board[x][y]
						board[x][y + 3] = "_"
			except IndexError:
				pass
	return board, total

images = ['```\n   +---+\n   O   | \n  /|\\  | \n  / \\  | \n      ===```',
		  '```\n   +---+ \n   O   | \n  /|\\  | \n  /    | \n      ===```',
		  '```\n   +---+ \n   O   | \n  /|\\  | \n       | \n      ===```',
		  '```\n   +---+ \n   O   | \n  /|   | \n       | \n      ===```',
		  '```\n   +---+ \n   O   | \n   |   | \n       | \n      ===```',
		  '```\n   +---+ \n   O   | \n       | \n       | \n      ===```',
		  '```\n  +---+ \n      | \n      | \n      | \n     ===```']

class Game(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		self.trivia = TriviaClient()
	#    self.owner = member
	 #   self.members = [member]
	  # self.possibleCards = []
	   # self.players = []
		#self.wagers = {}
		#self.roundCount = 0
		#self.gameID = None
		#self.cardToBeat = None
		#self.cardToBeatPlayerRef = None
		#self.startTrick = True
		#self.roomNum = None
		#self.room = None
		#self.winner = []
		#self.friendly = False
		#self.startRound = True
		#self.ctx = None

	@commands.command(name='2048')
	async def twenty(self, ctx):
		"""Play 2048 game"""
		await tplay(ctx, self.bot)
	
	@commands.command(name='minesweeper', aliases=['ms'])
	async def minesweeper(self, ctx, columns=None, rows=None, bombs=None):
		"""Play Minesweeper"""
		await mplay(ctx, columns, rows, bombs)

	@commands.command(name="rps")
	async def rock_paper_scissors(self, context):
		choices = {
			0: "rock",
			1: "paper",
			2: "scissors"
		}
		reactions = {
			"🪨": 0,
			"🧻": 1,
			"✂": 2
		}
		embed = discord.Embed(
			title="Rock Paper Scissors", color=discord.Color.random())
		embed.set_author(name=context.author.display_name,
						 icon_url=context.author.avatar_url)
		choose_message = await context.send(embed=embed)
		for emoji in reactions:
			await choose_message.add_reaction(emoji)

		def check(reaction, user):
			return user == context.message.author and str(reaction) in reactions

		try:
			reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=check)

			user_choice_emote = reaction.emoji
			user_choice_index = reactions[user_choice_emote]

			bot_choice_emote = random.choice(list(reactions.keys()))
			bot_choice_index = reactions[bot_choice_emote]

			result_embed = discord.Embed(color=discord.Color.random())
			result_embed.set_author(name=context.author.display_name,
									icon_url=context.author.avatar_url)
			await choose_message.clear_reactions()

			if user_choice_index == bot_choice_index:
				result_embed.description = f"`That's a Tie!`\nYou chose {user_choice_emote} and I chose {bot_choice_emote}."
				result_embed.colour = discord.color.red()
			elif user_choice_index == 0 and bot_choice_index == 2:
				result_embed.description = f"`You win!`\nYou chose {user_choice_emote} and I chose {bot_choice_emote}."
				result_embed.colour = discord.color.green()
			elif user_choice_index == 1 and bot_choice_index == 0:
				result_embed.description = f"`You win!`\nYou chose {user_choice_emote} and I chose {bot_choice_emote}."
				result_embed.colour = discord.color.green()
			elif user_choice_index == 2 and bot_choice_index == 1:
				result_embed.description = f"`You win!`\nYou chose {user_choice_emote} and I chose {bot_choice_emote}."
				result_embed.colour = discord.color.green()
			else:
				result_embed.description = f"`I win!`\nYou chose {user_choice_emote} and I chose {bot_choice_emote}."
				result_embed.colour = discord.Color.random()
				await choose_message.add_reaction("🇱")
			await choose_message.edit(embed=result_embed)
		except asyncio.exceptions.TimeoutError:
			await choose_message.clear_reactions()
			timeout_embed = discord.Embed(
				title="Time's Up!", color=discord.Color.random())
			timeout_embed.set_author(
				name=context.author.display_name, icon_url=context.author.avatar_url)
			await choose_message.edit(embed=timeout_embed)

	@commands.command(name='akinator')
	@commands.max_concurrency(1, per=BucketType.default)
	async def guess(self, ctx, *, category = None):

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
				if str(answer) in msg.content:
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

	@commands.command()
	async def scramble(self,ctx):
		'''Unscramble a word'''
		word = random.choice(words)
		l = list(word)
		scrambled = shuffle(l)
		y = ''.join(l)
		await ctx.reply(f"`Unscramble The Word : {y}`",allowed_mentions=discord.AllowedMentions(replied_user=False))
		msg = await self.bot.wait_for('message', timeout=15, check=lambda m: m.author == ctx.message.author)	

		if msg.content == word:
			await msg.reply('`That was Correct!`',allowed_mentions=discord.AllowedMentions(replied_user=False))
		else:
			await msg.reply(f"`that was wrong, the correct word was : {word}`",allowed_mentions=discord.AllowedMentions(replied_user=False))

	@commands.command()
	async def triviaboard(self,ctx):
		db = sqlite3.connect(r'C:\Users\HP\Desktop\yeetbot\cogs\db\trivia.sqlite', timeout=3)
		cursor = db.cursor()
		cursor.execute(f"SELECT member_id,score FROM main ORDER BY score DESC")
		embed = discord.Embed(title = 'Trivia Leaderboard', color = discord.Color.random())
		for i, pos in enumerate(cursor, start=1):
			member_id, score = pos

			if i == 1:
				i = "🥇"
			elif i == 2:
				i = '🥈'
			elif i == 3:
				i = '🥉'
			
			member = self.bot.get_user(member_id)
			embed.add_field(name=f'{i}.{member}', value=f'{score} Points', inline = False)
		
		await ctx.send(embed = embed)

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
				db = sqlite3.connect(r'C:\Users\HP\Desktop\yeetbot\cogs\db\fight.sqlite', timeout=3)
				cursor = db.cursor()
				cursor.execute(f"SELECT member_id, score FROM main WHERE member_id = {winner.id}")
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

	@commands.command()
	async def main(self, ctx):
		db = sqlite3.connect(
			r'C:\Users\HP\Desktop\yeetbot\cogs\db\fight.sqlite', timeout=3)
		cursor = db.cursor()
		cursor.execute(f"SELECT member_id,score FROM main ORDER BY score DESC")
		embed = discord.Embed(title='Fight Leaderboard',
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
			embed.add_field(name=f'{i}.{member}', value=f'{score} Points', inline=False)

		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Game(bot))
