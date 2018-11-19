import random
import sqlite3
import discord
import requests

from botutils import del_message
from discord.ext import commands
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

cd_json = 'http://sug.rocks/countdown/episodes.json'


class Utilities:
    """"Useful" commands"""
    def __init__(self, bot):
        self.bot = bot
        print('| Loaded:   utilities')

    @commands.command(pass_context=True, description='Example: "pizza or taco or burger".')
    async def pick(self, ctx, *, choices: str):
        """Pick an element, delimited by "or"."""
        author = ctx.message.author
        await self.bot.send_typing(ctx.message.channel)
        options = choices.split(' or ')
        if len(options) < 2:
            await self.bot.say('%s: I need two or more elements to choose.' % author.mention)
            return

        await self.bot.say('%s: %s' % (author.mention, random.choice(options)))

    @commands.command(pass_context=True, description='Add a name/mention as a parameter to know for someone else.')
    async def howlong(self, ctx, *, user: discord.Member=None):
        """Ask when someone joined the server."""
        author = ctx.message.author
        await self.bot.send_typing(ctx.message.channel)

        if user is None:
            user = author

        joined = user.joined_at.strftime('%b %d %Y at %I:%M:%S %p UTC')

        await self.bot.say('%s: %s joined this server %s' % (author.mention, user.name, joined))

    @commands.command(pass_context=True, description='Getting successfully bumps from ServerHound increment your score.')
    async def bumps(self, ctx):
        """See how many times you bumped the server."""
        db = sqlite3.connect('lilbutler.db')
        with db:
            db_cur = db.cursor()
            db_cur.execute("SELECT bumps FROM bumpers WHERE userId=? AND serverId=?", (ctx.message.author.id, ctx.message.server.id))
            row = db_cur.fetchone()

            if row is None:
                await self.bot.say('%s: You never bumped this server. :(' % ctx.message.author.mention)
            else:
                await self.bot.say('%s: You bumped this server %s times!' % (ctx.message.author.mention, str(row[0])))

    @commands.command(pass_context=True, description='Just to test if you\'re still there.')
    async def ping(self, ctx):
        """PONG!"""
        author = ctx.message.author

        try:
            await self.bot.send_typing(ctx.message.channel)
            await self.bot.say('%s: PONG !' % author.mention)
            await del_message(self, ctx)
        except Exception as e:
            await self.bot.say('%s: PONG ?' % author.mention)
            print('>>> ERROR Ping ', e)

    @commands.command(pass_context=True, description='Ask using the date in this format: YYYY-MM-DD')
    async def cn(self, ctx, *, param: str=None):
        """Get Cartoon Network's schedule"""
        author = ctx.message.author
        await self.bot.send_typing(ctx.message.channel)

        lstreq = requests.get('https://api.ctoon.network/schedule/days')
        lst = lstreq.json()

        if param is None:
            await self.bot.say('%s: Please specify a date (`~cn YYYY-MM-DD`). ' % author.mention)
            return

        if param not in lst:
            await self.bot.say('%s: Unknown date given (`~cn YYYY-MM-DD`).' % author.mention)
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
                await self.bot.say('%s: Unknown date given (`~cn YYYY-MM-DD`).' % author.mention)
                return

            em = discord.Embed(title='Schedule for ' + sch['date'] + ' (via ' + src_title + ')', colour=colour)

            for slot in sch[src][:20]:
                # We can't have more than 25 fields, let's cut at 20 and send the rest in a second message
                em.add_field(name=slot['time'], value='**' + slot['show'] + '**\n_' + slot['title'] + '_', inline=False)

            await self.bot.send_message(author, embed=em)

            # Send the second part
            if len(sch[src]) > 20:
                em = discord.Embed(colour=colour)

                for slot in sch[src][20:40]:
                    em.add_field(name=slot['time'], value='**' + slot['show'] + '**\n_' + slot['title'] + '_', inline=False)

                await self.bot.send_message(author, embed=em)

            # And third if needed
            if len(sch[src]) > 40:
                em = discord.Embed(colour=colour)

                for slot in sch[src][40:60]:
                    em.add_field(name=slot['time'], value='**' + slot['show'] + '**\n_' + slot['title'] + '_', inline=False)

                await self.bot.send_message(author, embed=em)

            # Heck, we never know!
            if len(sch[src]) > 60:
                em = discord.Embed(colour=colour)

                for slot in sch[src][60:]:
                    em.add_field(name=slot['time'], value='**' + slot['show'] + '**\n_' + slot['title'] + '_', inline=False)

                await self.bot.send_message(author, embed=em)

            # It's supposed to not tell the user to check their DMs when already in DM but oh well
            if ctx.message.channel is not None:
                await self.bot.say('%s: Please check your DMs.' % author.mention)
        except discord.errors.Forbidden:
            await self.bot.say('%s: It looks like you disabled DMs from strangers. I can\'t send the message.' % author.mention)

    @commands.command(pass_context=True, description='Will return a countdown.')
    async def countdown(self, ctx):
        """Time until next SU episode."""
        author = ctx.message.author

        try:
            await self.bot.send_typing(ctx.message.channel)
            cd = requests.get(cd_json).json()
            lines = ''
            postlimit = 0
            for ep in cd:
                if postlimit < 3:
                    now = datetime.now(timezone.utc)
                    then = datetime(ep['year'], ep['month'], ep['day'], ep['hour'], ep['minute'], tzinfo=timezone.utc)

                    if then < now:  # if episode is in the past, skip
                        continue

                    td = relativedelta(then, now)

                    countdown = ''

                    if td.months == 1:
                        countdown += "a month, "
                    elif td.months > 0:
                        countdown += str(td.months) + " months, "

                    if td.days == 1:
                        countdown += "a day, "
                    elif td.days > 0:
                        countdown += str(td.days) + " days, "

                    if td.hours == 1:
                        countdown += "1 hour and "
                    else:
                        countdown += str(td.hours) + " hours and "

                    if td.minutes == 1:
                        countdown += "1 minute "
                    else:
                        countdown += str(td.minutes) + " minutes"

                    if ep['leaked']:
                        notes = '(but already online)'
                    elif ep['supposed']:
                        notes = '(supposed)'
                    elif ep['app']:
                        notes = 'on the CN App'
                    else:
                        notes = ''

                    if ep['unknown']:
                        lines += '\n_%s_ (unknown date)' % ep['title']
                    else:
                        lines += '\n_%s_ will air in **%s** %s' % (ep['title'], countdown, notes)

                    postlimit += 1

            if postlimit == 0:
                await self.bot.say('%s: It looks like I don\'t know when the next episode is airing.' % author.mention)
            else:
                await self.bot.say('%s: %s' % (author.mention, lines))

        except Exception as e:
            await self.bot.say('%s: I\'m sorry, I can\'t help you with that right now.' % author.mention)
            print('>>> ERROR Countdown ', e)


def setup(bot):
    bot.add_cog(Utilities(bot))
