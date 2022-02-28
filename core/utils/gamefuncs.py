from typing import *
from discord.ext import commands
import random
from time import time
import asyncio
import discord
import asyncio
import random
from copy import deepcopy as dc

from discord.ext.commands.converter import MemberConverter

from akinator.async_aki import Akinator
import akinator


aki = Akinator()

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



	embed = discord.Embed(title='Minesweeper', color=discord.Color.random())
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
