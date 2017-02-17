import random
import requests
import sqlite3

from botutils import del_message
from discord.ext import commands
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

cd_epjs = 'https://sug.rocks/countdown/episodes.js'


class Utilities:
    """"Useful" commands"""
    def __init__(self, bot):
        print('extension loaded: utilities')
        self.bot = bot

    @commands.command(pass_context=True, description='Example: "pizza or taco or burger"')
    async def pick(self, ctx, *, choices: str):
        """Pick an element, delimited by "or"."""
        author = ctx.message.author
        await self.bot.send_typing(ctx.message.channel)
        options = choices.split(' or ')
        if len(options) < 2:
            await self.bot.say('%s: I need two or more elements to choose.' % author.mention)
            return

        await self.bot.say('%s: %s' % (author.mention, random.choice(options)))

    @commands.command(pass_context=True, description='Getting successfully bumps from ServerHound increment your score.')
    async def bumps(self, ctx):
        """See how many times you bumped the server"""
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

    @commands.command(pass_context=True, description='Will return a countdown.')
    async def countdown(self, ctx):
        """Time until next SU episode."""
        author = ctx.message.author

        try:
            await self.bot.send_typing(ctx.message.channel)
            cd = requests.get(cd_epjs, stream=True)
            postlimit = 0
            lines = ''
            for line in cd.iter_lines():
                if line and line.startswith(b'addEpisode(') and postlimit < 3:
                    ep = line.decode('utf-8').replace("addEpisode(", '')[:-1]
                    ep = [x.lstrip() for x in ep.split(',')]

                    now = datetime.now(timezone.utc)
                    then = datetime(int(ep[3]), int(ep[4]), int(ep[5]), int(ep[6]), int(ep[7]), tzinfo=timezone.utc)

                    if then < now:  # if episode is in the past, skip
                        continue

                    td = relativedelta(then, now)

                    if td.days == 1:
                        countdown = "a day, "
                    else:
                        countdown = str(td.days) + " days, "

                    if td.hours == 1:
                        countdown += "1 hour and "
                    else:
                        countdown += str(td.hours) + " hours and "

                    if td.minutes == 1:
                        countdown += "1 minute "
                    else:
                        countdown += str(td.minutes) + " minutes"

                    if ep[9] == '1':
                        notes = '(but already leaked)'
                    elif ep[10] == '1':
                        notes = '(supposed)'
                    else:
                        notes = ''

                    lines += '_%s_ will air in **%s** %s\n' % (ep[1][1:-1], countdown, notes)
                    postlimit += 1

            if postlimit == 0:
                await self.bot.say('%s: It looks like I don\'t know when the next episode is airing.' % author.mention)
            else:
                await self.bot.say('%s: %s' % (author.mention, lines))

        except Exception as e:
            await self.bot.say('%s: I\'m sorry, I can\'t help you with that.' % author.mention)
            print('>>> ERROR Countdown ', e)


def setup(bot):
    bot.add_cog(Utilities(bot))
