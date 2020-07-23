import discord
import configparser

from discord.ext import commands
from botutils import del_message, is_mod


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
    async def birthday(self, ctx, *, user: discord.Member = None, sid: int = 0):
        """Happy Birthday!"""
        if not is_mod(ctx.message):
            await ctx.send('%s: Sorry, but you\'re not allowed to do that.' % ctx.message.author.mention)
            return

        # Quit if no user mentioned or no id
        if user is None and sid == 0:
            await ctx.send('%s: I need to know who needs to get their roles changed.' % ctx.message.author.mention)
            return

        # If we don't mention someone, try to use the id instead
        if user is None:
            user = self.bot.fetch_user(sid)

        try:
            # await self.bot.send_typing(ctx.message.channel)
            user_roles = user.roles

            # Remove role (if found in user) and return
            for r in user.roles:
                if str(r.id) == self.conf.get('birthday', str(ctx.message.guild.id)):
                    user_roles.remove(r)
                    await user.edit(roles=user_roles)
                    await ctx.send('%s: Removed role.' % ctx.message.author.mention)
                    return

            # Add role and return
            for r in user.guild.roles:
                if str(r.id) == self.conf.get('birthday', str(ctx.message.guild.id)):
                    user_roles.append(r)
                    await user.edit(roles=user_roles)
                    await ctx.send('%s: Added role.' % ctx.message.author.mention)
                    return

        except Exception as e:
            print('>>> ERROR birthday ', e)

    @commands.command(description='But I might come back!')
    async def sleep(self, ctx):
        """Stops the bot."""
        if str(ctx.message.author.id) != self.conf.get('bot', 'owner_id'):
            await ctx.send('%s: Sorry, but you\'re not allowed to do that.' % ctx.message.author.mention)
            return

        await del_message(self, ctx)
        exit(0)  # I guess it crashes the app too, but whatever

    @commands.command(description='In case I went crazy...')
    async def clean(self, ctx):
        """Delete my own messages."""
        if not is_mod(ctx.message):
            await ctx.send('%s: Sorry, but you\'re not allowed to do that.' % ctx.message.author.mention)
            return

        try:
            # await self.bot.send_typing(ctx.message.channel)
            deleted = await ctx.message.channel.purge(before=ctx.message, limit=1000, check=self.is_me)
            if len(deleted) > 2:
                await ctx.send('Deleted %d messages.' % len(deleted))
            await del_message(self, ctx)
        except Exception as e:
            print('>>> ERROR clean ', e)

    @commands.command(description='Specify a number or I will clean the last 50 messages.')
    async def nuke(self, ctx, nbr: int = 50):
        """Delete a number of messages."""
        if not is_mod(ctx.message):
            await ctx.send('%s: Sorry, but you\'re not allowed to do that.' % ctx.message.author.mention)
            return

        try:
            # await self.bot.send_typing(ctx.message.channel)
            deleted = await ctx.message.channel.purge(before=ctx.message, limit=nbr)
            if len(deleted) > 2:
                await ctx.send('Deleted %d messages.' % len(deleted))
            await del_message(self, ctx)
        except Exception as e:
            print('>>> ERROR clean ', e)


def setup(bot):
    bot.add_cog(Mod(bot))
