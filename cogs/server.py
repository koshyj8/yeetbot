import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter


class Server(commands.Cog):
    """SERVER COMMANDS"""
    def __init__(self, bot):
        self.bot=bot

    @commands.command(name='perms')
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member: MemberConverter=None):
        """Check a users permissions"""

        if not member:
            member = ctx.author

        # Here we check if the value of each permission is True.
        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

        # And to make it look nice, we wrap it in an Embed.
        embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
        embed.set_author(icon_url=member.avatar, name=str(member))

        # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
        embed.add_field(
            name='**Permissions**', value='Administrator' if 'administrator' in perms else perms)

        await ctx.send(content=None, embed=embed)

    @commands.command(name='top_role')
    @commands.guild_only()
    async def show_toprole(self, ctx, *, member: MemberConverter = None):
        """Shows a member's top role"""

        if member is None:
            member = ctx.author

        await ctx.send(f'`The top role for {member.display_name} is {member.top_role.name}`')

async def setup(bot):
    await bot.add_cog(Server(bot))
