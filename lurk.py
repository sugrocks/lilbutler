import re
import random
import discord
import requests
from botutils import *
from datetime import datetime, timezone
from discord.ext import commands

cd_epjs = 'https://sug.rocks/countdown/episodes.js'

class Lurk:
    '''"Useful" commands'''
    def __init__(self, bot):
        print('extension loaded: lurk')
        self.bot = bot


    @commands.command(pass_context=True, description='Example: "pizza or taco or burger"')
    async def pick(self, ctx, *choices : str):
        '''Pick an element, delimited by "or"'''
        author = ctx.message.author
        await self.bot.send_typing(ctx.message.channel)
        options = ' '.join([str(x) for x in choices]).split(' or ')
        await self.bot.say('%s: %s' % (author.mention, random.choice(options)))
        await del_message(self, ctx)


    @commands.command(pass_context=True, description='Just to test if you\'re still there.')
    async def ping(self, ctx):
        '''PONG!'''
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
        '''Time until next SU episode.'''
        author = ctx.message.author

        try:
            await self.bot.send_typing(ctx.message.channel)
            cd = requests.get(cd_epjs, stream=True)
            postlimit = 0
            for line in cd.iter_lines():
                if line and line.startswith(b'addEpisode(') and postlimit < 3:
                    ep = line.decode('utf-8').replace("addEpisode(", '')[:-1]
                    ep = [x.lstrip() for x in ep.split(',')]
                    
                    now = datetime.now(timezone.utc)
                    then = datetime(int(ep[3]), int(ep[4]), int(ep[5]), int(ep[6]), int(ep[7]), tzinfo=timezone.utc)
                    if then < now: # if episode is in the past, skip
                        continue
                    td = then - now
                    countdown = ""
                    if td.days > 0:
                        countdown = str(td.days) + " days, "

                    if (td.seconds//3600) > 0:
                        countdown = countdown + str((td.seconds//3600)) + " hours and "

                    if (td.seconds//60)%60 == 1:
                        countdown = countdown + "1 minute "
                    else:
                        countdown = countdown + str((td.seconds//60)%60) + " minutes"

                    if ep[9] == '1':
                        notes = '(but already leaked)'
                    elif ep[10] == '1':
                        notes = '(supposed)'
                    else:
                        notes = ''

                    await self.bot.say('%s: *%s* will air in %s %s' % (author.mention, ep[1][1:-1], countdown, notes))
                    postlimit += 1

            if postlimit == 0:
                await self.bot.say('%s: It looks like I don\'t know when the next episode is airing.' % author.mention)

            await del_message(self, ctx)
        except Exception as e:
            await self.bot.say('%s: I\'m sorry, I can\'t help you with that.' % author.mention)
            print('>>> ERROR Countdown ', e)


def setup(bot):
    bot.add_cog(Lurk(bot))
