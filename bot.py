import os
import logging
import asyncio
import discord
import sqlite3
import configparser

from shutil import copyfile
from botutils import is_mod
from datetime import datetime
from discord.ext import commands
from dateutil.relativedelta import relativedelta

# Setup logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('@%(name)s [%(levelname)s] %(asctime)s: %(message)s'))
logger.addHandler(handler)

# Setup config
conf = configparser.ConfigParser()
conf.read('./config.ini')

# Setup discord-stuff
description = '"You people have too much money!"'
bot = commands.Bot(command_prefix='~', description=description)

# init
last_bumper = None
db = None


# On bot login
@bot.event
async def on_ready():
    print('I\'m ' + bot.user.name + '!')
    print('ID: ' + bot.user.id)
    print('------------------')
    # Import our 'modules'
    bot.load_extension('utilities')
    bot.load_extension('mod')


# On new messages
@bot.event
async def on_message(message):
    global last_bumper

    # Remove messages if they're in the blacklist
    blacklist = ['discord.gg', 'discordapp.com/invite']
    if any(thing in message.content for thing in blacklist) and not is_mod(message):
        await bot.delete_message(message)
        return

    if message.content.startswith('=bump'):
        last_bumper = message.author

    if last_bumper is not None and message.author.id == '222853335877812224' and message.content.startswith('Bumped!'):
        with db:
            db_cur = db.cursor()
            db_cur.execute("SELECT bumps FROM bumpers WHERE userId=? AND serverId=?", (last_bumper.id, message.server.id))
            row = db_cur.fetchone()

            # Did that person bump once?
            if row is None:
                # If not, add it to the DB with the value of "1"
                db_cur.execute("INSERT INTO bumpers(userId, serverId, bumps) VALUES(?, ?, 1)", (last_bumper.id, message.server.id))
                bump_score = 'This is your first bump here! You can use `~bumps` to see your score.'
            else:
                # If yes, increment value
                c = int(row[0]) + 1
                db_cur.execute("UPDATE bumpers SET bumps=? WHERE userId=? AND serverId=?", (c, last_bumper.id, message.server.id))
                if c == 2:
                    bump_score = 'This is your second bump, keep going!'
                elif c == 3:
                    bump_score = 'A third bump? How nice of you. :)'
                elif c == 10:
                    bump_score = 'This is your tenth bump! Woo!'
                elif c == 25:
                    bump_score = 'You bumped this server 25 times! Pretty impressive.'
                elif c == 50:
                    if last_bumper.id == '173498245656477696':
                        bump_score = 'So, MP. That\'s 50 times. I guess nothing can stop you now.'
                    else:
                        bump_score = 'You bumped this server 50 times, time to hit the hundredth!'
                elif c == 90:
                    bump_score = 'You bumped this server 90 times.\n _Bumping in the 90\'s_ 🎶'
                elif c == 100:
                    bump_score = 'Behold. A new **bump master** arrived, with 100 bumps to their score!'
                elif c == 200:
                    bump_score = 'Dude what. 200 times? That\'s determination.'
                else:
                    bump_score = 'You bumped this server %s times.' % (str(c))

        await bot.send_message(message.channel, 'Thank you, %s! %s' % (last_bumper.mention, bump_score))

    # And now go to the bot commands
    await bot.process_commands(message)


# On user join
@bot.event
async def on_member_join(member):
    # Notify in defined channel for the server
    server = member.server

    try:
        chan = conf.get('modlogs', str(server.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # If there's nothing, don't do anything

    # Build an embed
    em = discord.Embed(title=member.name + ' joined the server', description='Say hi to ' + member.mention,
                       colour=0x23D160, timestamp=datetime.utcnow())  # color: green
    em.set_thumbnail(url=member.avatar_url)
    em.set_footer(text='ID: ' + str(member.id))

    # Send message with embed
    await bot.send_message(discord.Object(int(chan)), embed=em)


# On user leave
@bot.event
async def on_member_remove(member):
    # Notify in defined channel for the server
    server = member.server

    try:
        chan = conf.get('modlogs', str(server.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # If there's nothing, don't do anything

    # Count for how long an user has been a member
    diff = relativedelta(datetime.utcnow(), member.joined_at)
    member_since = member.mention + ' was a member for %d months, %d days, %d hours, %d minutes and %d seconds.' % (
        diff.months, diff.days, diff.hours, diff.minutes, diff.seconds)

    # Build an embed
    em = discord.Embed(title=member.name + ' left the server', description=member_since,
                       colour=0xE81010, timestamp=datetime.utcnow())  # color: red
    em.set_thumbnail(url=member.avatar_url)
    em.set_footer(text='ID: ' + str(member.id))

    # Send message with embed
    await bot.send_message(discord.Object(int(chan)), embed=em)


# On user ban
@bot.event
async def on_member_ban(member):
    # Notify in defined channel for the server
    server = member.server

    try:
        chan = conf.get('modlogs', str(server.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # If there's nothing, don't do anything

    # Build an embed
    em = discord.Embed(title=member.name + ' is now banned from the server',
                       colour=0x7289DA, timestamp=datetime.utcnow())  # color: blue
    em.set_thumbnail(url=member.avatar_url)
    em.set_footer(text='ID: ' + str(member.id))

    # Send message with embed
    await bot.send_message(discord.Object(int(chan)), embed=em)


async def clean_temp():
    await bot.wait_until_ready()

    while not bot.is_closed:
        conf.read('./config.ini')  # re-read, in case we changed something
        channels = dict(conf.items('cleantemp'))

        for channel in channels:
            chan = bot.get_channel(channel)

            async for message in bot.logs_from(chan, limit=100, reverse=True):  # load logs with 100 messages
                deleted = await bot.purge_from(chan, before=message)  # delete anything above that 100 messages count
                if len(deleted) > 0:  # log in console that it deleted stuff
                    print(str(channel) + ' deleted ' + str(len(deleted)) + ' messages')

                break  # we only needed the first message in log, actually

        await asyncio.sleep(60 * 15)  # sleep 15 minutes


# Launch
if __name__ == '__main__':
    try:
        # If there's no database file, copy from the empty one
        if not os.path.isfile('lilbutler.db'):
            copyfile('lilbutler.empty.db', 'lilbutler.db')

        # Connect to SQLite3 DB
        db = sqlite3.connect('lilbutler.db')
        with db:
            cur = db.cursor()
            cur.execute('SELECT SQLITE_VERSION()')
            data = cur.fetchone()
            print("SQLite version: %s" % data)
    except Exception as e:
        print("Error : " + str(e))
        exit(1)

    bot.loop.create_task(clean_temp())
    bot.run(conf.get('bot', 'token'))
