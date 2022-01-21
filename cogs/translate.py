
from discord.ext import commands
import discord

from typing import List, Optional, Union
import asyncio
import googletrans

from core.utils.pagin import *

langs = {
		'af': 'afrikaans',
		'sq': 'albanian',
		'am': 'amharic',
		'ar': 'arabic',
		'hy': 'armenian',
		'az': 'azerbaijani',
		'eu': 'basque',
		'be': 'belarusian',
		'bn': 'bengali',
		'bs': 'bosnian',
		'bg': 'bulgarian',
		'ca': 'catalan',
		'ceb': 'cebuano',
		'ny': 'chichewa',
		'zh-cn': 'chinese (simplified)',
		'zh-tw': 'chinese (traditional)',
		'co': 'corsican',
		'hr': 'croatian',
		'cs': 'czech',
		'da': 'danish',
		'nl': 'dutch',
		'en': 'english',
		'eo': 'esperanto',
		'et': 'estonian',
		'tl': 'filipino',
		'fi': 'finnish',
		'fr': 'french',
		'fy': 'frisian',
		'gl': 'galician',
		'ka': 'georgian',
		'de': 'german',
		'el': 'greek',
		'gu': 'gujarati',
		'ht': 'haitian creole',
		'ha': 'hausa',
		'haw': 'hawaiian',
		'iw': 'hebrew',
		'he': 'hebrew',
		'hi': 'hindi',
		'hmn': 'hmong',
		'hu': 'hungarian',
		'is': 'icelandic',
		'ig': 'igbo',
		'id': 'indonesian',
		'ga': 'irish',
		'it': 'italian',
		'ja': 'japanese',
		'jw': 'javanese',
		'kn': 'kannada',
		'kk': 'kazakh',
		'km': 'khmer',
		'ko': 'korean',
		'ku': 'kurdish (kurmanji)',
		'ky': 'kyrgyz',
		'lo': 'lao',
		'la': 'latin',
		'lv': 'latvian',
		'lt': 'lithuanian',
		'lb': 'luxembourgish',
		'mk': 'macedonian',
		'mg': 'malagasy',
		'ms': 'malay',
		'ml': 'malayalam',
		'mt': 'maltese',
		'mi': 'maori',
		'mr': 'marathi',
		'mn': 'mongolian',
		'my': 'myanmar (burmese)',
		'ne': 'nepali',
		'no': 'norwegian',
		'or': 'odia',
		'ps': 'pashto',
		'fa': 'persian',
		'pl': 'polish',
		'pt': 'portuguese',
		'pa': 'punjabi',
		'ro': 'romanian',
		'ru': 'russian',
		'sm': 'samoan',
		'gd': 'scots gaelic',
		'sr': 'serbian',
		'st': 'sesotho',
		'sn': 'shona',
		'sd': 'sindhi',
		'si': 'sinhala',
		'sk': 'slovak',
		'sl': 'slovenian',
		'so': 'somali',
		'es': 'spanish',
		'su': 'sundanese',
		'sw': 'swahili',
		'sv': 'swedish',
		'tg': 'tajik',
		'ta': 'tamil',
		'te': 'telugu',
		'th': 'thai',
		'tr': 'turkish',
		'uk': 'ukrainian',
		'ur': 'urdu',
		'ug': 'uyghur',
		'uz': 'uzbek',
		'vi': 'vietnamese',
		'cy': 'welsh',
		'xh': 'xhosa',
		'yi': 'yiddish',
		'yo': 'yoruba',
		'zu': 'zulu'}

class Translate(commands.Cog):
	'''TRANSLATE COMMANDS'''
	def __init__(self, bot ):
		self.bot = bot
		self.to_morse = {
					"a": ".-",
							"b": "-...",
							"c": "-.-.",
							"d": "-..",
							"e": ".",
							"f": "..-.",
							"g": "--.",
							"h": "....",
							"i": "..",
							"j": ".---",
							"k": "-.-",
							"l": ".-..",
							"m": "--",
							"n": "-.",
							"o": "---",
							"p": ".--.",
							"q": "--.-",
							"r": ".-.",
							"s": "...",
							"t": "-",
							"u": "..-",
							"v": "...-",
							"w": ".--",
							"x": "-..-",
							"y": "-.--",
							"z": "--..",
							"1": ".----",
							"2": "..---",
							"3": "...--",
							"4": "....-",
							"5": ".....",
							"6": "-....",
							"7": "--...",
							"8": "---..",
							"9": "----.",
							"0": "-----"
				}

	@commands.command(pass_context=True)
	async def morsetable(self, ctx):
		"""Morse Code Table"""

		await ctx.send('https://images.sampletemplates.com/wp-content/uploads/2015/09/Morse-Code-Alphabet.jpg?width=480')

	@commands.command(pass_context=True)
	async def morse(self, ctx, *, text):
		"""Converts ascii to morse code"""

		word_list = text.split()
		morse_list = []
		for word in word_list:
			letter_list = []
			for letter in word:

				if letter.lower() in self.to_morse:

					letter_list.append(self.to_morse[letter.lower()])
			if len(letter_list):

				morse_list.append(" ".join(letter_list))

		if not len(morse_list):

			await ctx.send("`There were no valid non-morse words.`")
			return

		msg = "    ".join(morse_list)
		msg = "\n" + msg + ""
		await ctx.send(f"`{msg}`")

	@commands.command(pass_context=True)
	async def unmorse(self, ctx, *, content=None):
		"""Converts morse code to ascii."""

		content = "".join([x for x in content if x in " .-"])
		word_list = content.split("    ")
		ascii_list = []
		for word in word_list:

			letter_list = word.split()
			letter_ascii = []

			for letter in letter_list:
				for key in self.to_morse:
					if self.to_morse[key] == letter:

						letter_ascii.append(key.upper())
			if len(letter_ascii):

				ascii_list.append("".join(letter_ascii))

		if not len(ascii_list):

			await ctx.send("`There were no valid morse words.`")
			return

		msg = " ".join(ascii_list)
		msg = "\n" + msg + ""
		await ctx.send(f"`{msg}`")

	@commands.command(aliases=['tr'])
	async def translate(self,ctx, lang_to, *args):
		lang_to = lang_to.lower()
		if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
			print(f"That is not a valid Language")

		text = ' '.join(args)
		translator = googletrans.Translator()
		translated = translator.translate(text, dest=lang_to).text
		await ctx.send(f"`{translated}`")

def setup(bot):
	bot.add_cog(Translate(bot))
