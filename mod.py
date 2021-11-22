import discord
import configparser

from discord.ext import commands
from botutils import is_mod, reply


class Mod(commands.Cog):
    """Commands for mods."""
    def __init__(self, bot):
        self.bot = bot
        self.conf = configparser.ConfigParser()
        self.conf.read('./config.ini')
        print('| Loaded:   mod')

    def is_me(self, message):
        return message.author == self.bot.user

    @commands.command(description='Toggle the birthday role, if available.')
    async def birthday(self, ctx, user: discord.Member = None):
        """Happy Birthday!"""
        # await ctx.respond(eat=True)

        if not is_mod(ctx.channel, ctx.author):
            await reply(ctx, 'Sorry but you\'re not allowed to do that.', ephemeral=True)
            return

        # Quit if we can't get the user
        if user is None:
            await reply(ctx, 'I can\'t get the user :(', ephemeral=True)
            return

        try:
            # await ctx.trigger_typing()
            user_roles = user.roles

            # Remove role (if found in user) and return
            for r in user.roles:
                if str(r.id) == self.conf.get('birthday', str(ctx.guild.id)):
                    user_roles.remove(r)
                    await user.edit(roles=user_roles)
                    await reply(ctx, 'Birthday time is over.', ephemeral=True)
                    return

            # Add role and return
            for r in user.guild.roles:
                if str(r.id) == self.conf.get('birthday', str(ctx.guild.id)):
                    user_roles.append(r)
                    await user.edit(roles=user_roles)
                    await reply(ctx, 'Happy birthday %s!' % user.mention)
                    return

        except Exception as e:
            print('>>> ERROR birthday ', e)

    @commands.command(description='But I might come back!')
    async def sleep(self, ctx):
        """Stops the bot."""
        if str(ctx.author.id) != self.conf.get('bot', 'owner_id'):
            await reply(ctx, 'Sorry but you\'re not allowed to do that.', ephemeral=True)
            return

        await reply(ctx, 'Goodnight.', ephemeral=True)
        exit(0)  # I guess it crashes the app too, but whatever

    @commands.command(description='In case I went crazy...')
    async def clean(self, ctx):
        """Delete my own messages."""
        if not is_mod(ctx.message.channel, ctx.author):
            await reply(ctx, 'Sorry but you\'re not allowed to do that.', ephemeral=True)
            return

        try:
            await ctx.trigger_typing()
            deleted = await ctx.message.channel.purge(before=ctx.message, limit=1000, check=self.is_me)
            if len(deleted) > 2:
                await reply(ctx, 'Deleted %d of my own messages.' % len(deleted), ephemeral=True)
        except Exception as e:
            print('>>> ERROR clean ', e)

    @commands.command(description='Specify a number or I will clean the last 50 messages.')
    async def nuke(self, ctx, nbr: int = 50):
        """Delete a number of messages."""
        if not is_mod(ctx.message.channel, ctx.author):
            await reply(ctx, 'Sorry but you\'re not allowed to do that.', ephemeral=True)
            return

        try:
            await ctx.trigger_typing()
            deleted = await ctx.message.channel.purge(before=ctx.message, limit=nbr)
            if len(deleted) > 2:
                await reply(ctx, 'Deleted %d messages.' % len(deleted), ephemeral=True)
        except Exception as e:
            print('>>> ERROR clean ', e)


def setup(bot):
    bot.add_cog(Mod(bot))
