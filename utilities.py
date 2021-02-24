import random
import discord
import requests

from discord.ext import commands


class Utilities(commands.Cog):
    """"Useful" commands"""
    def __init__(self, bot):
        self.bot = bot
        print('| Loaded:   utilities')

    @commands.command(description='Example: "pizza or taco or burger".')
    async def pick(self, ctx, *, choices: str):
        """Pick an element, delimited by "or"."""
        author = ctx.message.author
        await ctx.trigger_typing()
        options = choices.split(' or ')
        if len(options) < 2:
            await ctx.reply('I need two or more elements to choose from.')
            return

        await ctx.reply(random.choice(options))

    @commands.command(description='Add a name/mention as a parameter to know for someone else.')
    async def howlong(self, ctx, *, user: discord.Member = None):
        """Ask when someone joined the server."""
        author = ctx.message.author
        await ctx.trigger_typing()

        if user is None:
            user = author

        joined = user.joined_at.strftime('%b %d %Y at %I:%M:%S %p UTC')

        await ctx.reply('%s joined this server %s' % (user.name, joined))

    @commands.command(description='Just to test if you\'re still there.')
    async def ping(self, ctx):
        """PONG!"""
        author = ctx.message.author

        try:
            await ctx.trigger_typing()
            await ctx.reply('PONG !')
        except Exception as e:
            await ctx.send('PONG ?')
            print('>>> ERROR Ping ', e)

    @commands.command(description='Ask using the date in this format: YYYY-MM-DD')
    async def cn(self, ctx, *, param: str = None):
        """Get Cartoon Network's schedule"""
        author = ctx.message.author
        await ctx.trigger_typing()

        lstreq = requests.get('https://api.ctoon.network/schedule/days')
        lst = lstreq.json()

        if param is None:
            await ctx.reply('Please specify a date (`~cn YYYY-MM-DD`).')
            return

        if param not in lst:
            await ctx.reply('Unknown date given (`~cn YYYY-MM-DD`).')
            return

        schreq = requests.get('https://api.ctoon.network/schedule/day/%s' % param)
        sch = schreq.json()

        # Send message with embed
        try:
            if sch['cn'] is not None:
                src = 'cn'
                src_title = 'Cartoon Network'
                colour = 0xEC018C  # color: CN's pink
            elif sch['tvguide'] is not None:
                src = 'tvguide'
                src_title = 'TV Guide'
                colour = 0xACFFAD  # color: Zap2it Green
            elif sch['zap'] is not None:
                src = 'zap'
                src_title = 'Zap2it'
                colour = 0xACFFAD  # color: Zap2it Green
            else:
                await ctx.reply('Unknown date given (`~cn YYYY-MM-DD`).')
                return

            em = discord.Embed(title='Schedule for ' + sch['date'] + ' (via ' + src_title + ')', colour=colour)

            for slot in sch[src][:20]:
                # We can't have more than 25 fields, let's cut at 20 and send the rest in a second message
                em.add_field(name=slot['time'], value='**' + slot['show'] + '**\n_' + slot['title'] + '_', inline=False)

            await author.send(embed=em)

            # Send the second part
            if len(sch[src]) > 20:
                em = discord.Embed(colour=colour)

                for slot in sch[src][20:40]:
                    em.add_field(name=slot['time'], value='**' + slot['show'] + '**\n_' + slot['title'] + '_', inline=False)

                await author.send(embed=em)

            # And third if needed
            if len(sch[src]) > 40:
                em = discord.Embed(colour=colour)

                for slot in sch[src][40:60]:
                    em.add_field(name=slot['time'], value='**' + slot['show'] + '**\n_' + slot['title'] + '_', inline=False)

                await author.send(embed=em)

            # Heck, we never know!
            if len(sch[src]) > 60:
                em = discord.Embed(colour=colour)

                for slot in sch[src][60:]:
                    em.add_field(name=slot['time'], value='**' + slot['show'] + '**\n_' + slot['title'] + '_', inline=False)

                await author.send(embed=em)

            # It's supposed to not tell the user to check their DMs when already in DM but oh well
            if ctx.message.channel is not None:
                await ctx.reply('Please check your DMs.')
        except discord.errors.Forbidden:
            await ctx.reply('It looks like you disabled DMs from strangers. I can\'t send the message.')


def setup(bot):
    bot.add_cog(Utilities(bot))
