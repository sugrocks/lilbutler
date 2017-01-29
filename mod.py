import discord
from botutils import *
from discord.ext import commands


class Mod:
    '''Commands for mods.'''
    def __init__(self, bot):
        print('extension loaded: mod')
        self.bot = bot


    def is_me(self, m):
        return m.author == self.bot.user


    @commands.command(pass_context=True, description='In case I went crazy...')
    async def clean(self, ctx):
        '''Delete my own messages.'''
        if not is_mod(ctx):
            return

        try:
            await self.bot.send_typing(ctx.message.channel)
            deleted = await self.bot.purge_from(ctx.message.channel, limit=1000, check=self.is_me)
            if len(deleted) > 2:
                await self.bot.say('%d deleted messages.' % len(deleted))
            await del_message(self, ctx)
        except Exception as e:
            print('>>> ERROR clean ', e)


    @commands.command(pass_context=True,
        description='Specify a number to tell how many messages I\'ll clean.. Or don\'t and I\'ll remove the last 50 ones.')
    async def nuke(self, ctx, nbr : int = 50):
        '''Delete a number of messages.'''
        if not is_mod(ctx):
            return

        try:
            await self.bot.send_typing(ctx.message.channel)
            deleted = await self.bot.purge_from(ctx.message.channel, limit=nbr)
            if len(deleted) > 2:
                await self.bot.say('%d deleted messages.' % len(deleted))
            await del_message(self, ctx)
        except Exception as e:
            print('>>> ERROR clean ', e)


def setup(bot):
    bot.add_cog(Mod(bot))
