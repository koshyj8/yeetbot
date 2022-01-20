from discord.ext import commands

class Server(commands.Cog):
    """SERVER COMMANDS"""
    def __init__(self, bot):
        self.bot=bot



def setup(bot):
    bot.add_cog(Server(bot))