import configparser

from discord.ext import commands
from botutils import del_message, is_mod


class Mod:
    """Commands for mods."""
    def __init__(self, bot):
        self.bot = bot
        self.conf = configparser.ConfigParser()
        self.conf.read('./config.ini')
        print('| Loaded:   mod')

    def is_me(self, message):
        return message.author == self.bot.user

    @commands.command(pass_context=True, description='But I might come back!')
    async def sleep(self, ctx):
        """Stops the bot."""
        if ctx.message.author.id != self.conf.get('bot', 'owner_id'):
            await self.bot.say('%s: Sorry, but you\'re not allowed to do that.' % ctx.message.author.mention)
            return

        await del_message(self, ctx)
        exit(0)  # I guess it crashes the app too, but whatever

    @commands.command(pass_context=True, description='In case I went crazy...')
    async def clean(self, ctx):
        """Delete my own messages."""
        if not is_mod(ctx.message):
            await self.bot.say('%s: Sorry, but you\'re not allowed to do that.' % ctx.message.author.mention)
            return

        try:
            await self.bot.send_typing(ctx.message.channel)
            deleted = await self.bot.purge_from(ctx.message.channel, before=ctx.message, limit=1000, check=self.is_me)
            if len(deleted) > 2:
                await self.bot.say('Deleted %d messages.' % len(deleted))
            await del_message(self, ctx)
        except Exception as e:
            print('>>> ERROR clean ', e)

    @commands.command(pass_context=True, description='Specify a number or I will clean the last 50 messages.')
    async def nuke(self, ctx, nbr: int = 50):
        """Delete a number of messages."""
        if not is_mod(ctx.message):
            await self.bot.say('%s: Sorry, but you\'re not allowed to do that.' % ctx.message.author.mention)
            return

        try:
            await self.bot.send_typing(ctx.message.channel)
            deleted = await self.bot.purge_from(ctx.message.channel, before=ctx.message, limit=nbr)
            if len(deleted) > 2:
                await self.bot.say('Deleted %d messages.' % len(deleted))
            await del_message(self, ctx)
        except Exception as e:
            print('>>> ERROR clean ', e)


def setup(bot):
    bot.add_cog(Mod(bot))
