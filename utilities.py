import random
import discord
import requests

from discord.ext import commands
from botutils import reply


class Utilities(commands.Cog):
    """"Useful" commands"""
    def __init__(self, bot):
        self.bot = bot
        print('| Loaded:   utilities')

    @commands.command(description='Example: "pizza, taco, burger".')
    async def pick(self, ctx, *, list: str):
        """Pick an element, delimited by ","."""
        await ctx.trigger_typing()
        options = list.split(',')
        if len(options) < 2:
            await reply(ctx, 'I need two or more elements to choose from.', ephemeral=True)
            return

        await reply(ctx, 'In `' + list.replace('`', "'") + '`:\n' + random.choice(options).strip())

    @commands.command(description='Add a name/mention as a parameter to know for someone else.')
    async def howlong(self, ctx, *, user: discord.Member = None):
        """Ask when someone joined the server."""
        await ctx.trigger_typing()

        if user is None:
            user = ctx.author

        # joined = user.joined_at.strftime('%b %d %Y at %I:%M:%S %p UTC')
        joined = '<t:' + str(int(user.joined_at.timestamp())) + ':F>'

        await reply(ctx, '%s joined this server %s' % (user.name, joined))

    @commands.command(description='Just to test if you\'re still there.')
    async def ping(self, ctx):
        """PONG!"""
        try:
            await ctx.trigger_typing()
            await reply(ctx, 'PONG !')
        except Exception as e:
            await ctx.send('PONG ?')
            print('>>> ERROR Ping ', e)

    @commands.command(description='Ask using the date in this format: YYYY-MM-DD')
    async def cn(self, ctx, *, date: str = None):
        """Get Cartoon Network's schedule"""
        author = ctx.author
        await ctx.trigger_typing()

        if date is None:
            await reply(ctx, 'Please specify a date (`~cn YYYY-MM-DD`).', ephemeral=True)
            return

        lstreq = requests.get('https://api.ctoon.network/schedule/v2/days')
        lst = lstreq.json()

        if date not in lst:
            await reply(ctx, 'Unknown date given (`~cn YYYY-MM-DD`).', ephemeral=True)
            return

        schreq = requests.get('https://api.ctoon.network/schedule/v2/day/%s' % date)
        sch = schreq.json()

        # Send message with embed
        try:
            if sch['schedule']['cn'] is not None:
                src = 'cn'
                src_title = 'Cartoon Network'
                colour = 0xEC018C  # color: CN's pink
            elif sch['schedule']['tvguide'] is not None:
                src = 'tvguide'
                src_title = 'TV Guide'
                colour = 0xACFFAD  # color: Zap2it Green
            elif sch['schedule']['zap'] is not None:
                src = 'zap'
                src_title = 'Zap2it'
                colour = 0xACFFAD  # color: Zap2it Green
            else:
                await reply(ctx, 'No data for date given (`~cn YYYY-MM-DD`).', ephemeral=True)
                return

            em = discord.Embed(title='Schedule for ' + sch['date'] + ' (via ' + src_title + ')', colour=colour)

            for slot in sch['schedule'][src][:20]:
                # We can't have more than 25 fields, let's cut at 20 and send the rest in a second message
                em.add_field(name=slot['time'], value='**' + str(slot['show']) + '**\n_' + str(slot['title']) + '_', inline=False)

            await author.send(embed=em)

            # Send the second part
            if len(sch['schedule'][src]) > 20:
                em = discord.Embed(colour=colour)

                for slot in sch['schedule'][src][20:40]:
                    em.add_field(name=slot['time'], value='**' + str(slot['show']) + '**\n_' + str(slot['title']) + '_', inline=False)

                await author.send(embed=em)

            # And third if needed
            if len(sch['schedule'][src]) > 40:
                em = discord.Embed(colour=colour)

                for slot in sch['schedule'][src][40:60]:
                    em.add_field(name=slot['time'], value='**' + str(slot['show']) + '**\n_' + str(slot['title']) + '_', inline=False)

                await author.send(embed=em)

            # Heck, we never know!
            if len(sch['schedule'][src]) > 60:
                em = discord.Embed(colour=colour)

                for slot in sch['schedule'][src][60:]:
                    em.add_field(name=slot['time'], value='**' + str(slot['show']) + '**\n_' + str(slot['title']) + '_', inline=False)

                await author.send(embed=em)

            # It's supposed to not tell the user to check their DMs when already in DM but oh well
            if not isinstance(ctx, discord.ext.commands.context.SlashContext):
                if ctx.message.channel is not None:
                    await reply(ctx, 'Please check your DMs.', ephemeral=True)
            else:
                await reply(ctx, 'Please check your DMs.', ephemeral=True)
        except discord.errors.Forbidden:
            await reply(ctx, 'It looks like you disabled DMs from strangers. I can\'t send the message.', ephemeral=True)


def setup(bot):
    bot.add_cog(Utilities(bot))
