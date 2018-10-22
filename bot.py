import os
import time
import json
import random
import logging
import asyncio
import aiohttp
import discord
import sqlite3
import requests
import humanize
import configparser
import better_exceptions

from shutil import copyfile
from botutils import is_mod
from datetime import datetime, timedelta
from discord import utils as dutils
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
bot = commands.Bot(max_messages=15000, command_prefix='~', description=description, pm_help=True)

# init
better_exceptions.MAX_LENGTH = None
whitelisted_servers = conf.get('bot', 'whitelist').split(',')
last_bumper = None
db = None
sqlite_version = '???'
server_bump_wait = {}
banlist = []
invites = {}
banned_names = ['discord.gg', 'free games', 'discord.io', 'discord.me', 'invite.gg', 'twitch.tv', 'twitter.com']
delete_content = []


# dbans
async def checkBan(userid):
    headers = {'Authorization': conf.get('bot', 'dbans')}
    url = 'https://bans.discord.id/api/check.php?user_id=' + userid

    async with aiohttp.ClientSession() as session:
        resp = await session.get(url, headers=headers)
        final = await resp.text()
        resp.close()

    data = json.loads(final)
    result = []
    for s in data:
        if s['banned'] == '1':
            result.append({'id': s['case_id'], 'reason': s['reason'], 'proof': s['proof']})

    return result


# On bot login
@bot.event
async def on_ready():
    s = bot.servers
    exitme = False
    for server in s:
        try:
            if server.id not in whitelisted_servers:
                print(server.name + ' (by ' + server.owner.name + '#' + str(server.owner.discriminator) + ') not in whitelist, leaving.')
                exitme = True
                await bot.leave_server(server)
        except:
            pass

    if exitme:
        bot.close()
        exit(0)

    print('/-----------------------------------------------------------------------------')
    print('| # ME')
    print('| Name:     ' + bot.user.name)
    print('| ID:       ' + bot.user.id)
    print('| Invite:   https://discord.now.sh/' + bot.user.id + '?p1543892215')
    print('| SQLite:   ' + sqlite_version)
    print('|-----------------------------------------------------------------------------')
    print('| # MODULES')
    # Import our 'modules'
    bot.load_extension('utilities')
    bot.load_extension('mod')
    print('|-----------------------------------------------------------------------------')
    print('| # SERVERS (' + str(len(bot.servers)) + ')')
    for server in bot.servers:
        print('| > Name:   ' + server.name + ' (' + server.id + ')')
        print('|   Owner:  ' + server.owner.name + '#' + str(server.owner.discriminator))
        if server.me.nick:
            print('|   Nick:   ' + server.me.nick)
    print('\-----------------------------------------------------------------------------')


# On new messages
@bot.event
async def on_message(message):
    global last_bumper

    # Remove messages if they're in the blacklist
    blacklist = ['discord.gg', 'discordapp.com/invite']
    if any(thing in message.content for thing in blacklist) and not is_mod(message):
        await bot.delete_message(message)
        return

    # Remove messages if they're in the delete queue
    for w in delete_content:
        if w in message.content:
            await bot.delete_message(message)
            delete_content.remove(w)
            return

    if message.content.startswith('=bump'):
        last_bumper = message.author

    if last_bumper is not None and message.author.id == '222853335877812224' and message.content.startswith('Bumped!'):
        if message.server.id in server_bump_wait:
            # Don't count in the server if last bump was under 30 minutes (fix against lag from the bump bot)
            if int(datetime.now().timestamp()) < server_bump_wait[message.server.id] + 1800:
                return

        # Save timestamp since last bump
        server_bump_wait[message.server.id] = int(datetime.now().timestamp())

        # A list of happy emojis when someone bump the server
        emojis = ['💃', '😎', '🙏', '🙌', '👏', '👍', '😁']

        with db:
            # Let's get informations about our user in this server...
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

                # And let's display a nice message
                if c == 2:
                    bump_score = 'This is your second bump, keep going!'
                elif c == 3:
                    bump_score = 'A third bump? How nice of you. :)'
                elif c == 10:
                    bump_score = 'This is your tenth bump! Woo!'
                elif c == 25:
                    bump_score = 'You bumped this server 25 times! Pretty impressive.'
                elif c == 50:
                    bump_score = 'You bumped this server 50 times, time to hit the hundredth!'
                elif c == 69:
                    bump_score = 'You bumped this server 👀 times.'
                elif c == 90:
                    bump_score = 'You bumped this server 90 times.\n _Bumping in the 90\'s_ 🎶\nhttps://www.youtube.com/watch?v=XCiDuy4mrWU'
                elif c == 100:
                    bump_score = 'Behold. A new **bump master** arrived, with 100 bumps to their score!'
                elif c == 200:
                    bump_score = 'Dude what. 200 times? That\'s determination.'
                elif c == 300:
                    bump_score = 'THIS. IS. SPARTA!'
                elif c == 301:
                    bump_score = 'The hell are you doing???'
                elif c == 302:
                    bump_score = 'Like, stop.'
                elif c == 303:
                    bump_score = 'How did you bump this much?'
                elif c == 304:
                    bump_score = 'To get to this number of bumps (304), you waited **AT LEAST** 912 hours, that\'s 38 days.'
                elif c == 305:
                    bump_score = 'Welp. 305'
                elif c == 306:
                    bump_score = 'And 306...'
                elif c == 307:
                    bump_score = '307. You\'re leaving me depressed.'
                elif c == 308:
                    bump_score = 'Aaaaaaaand 308.'
                elif c == 309:
                    bump_score = 'Here comes 309.'
                elif c == 310:
                    bump_score = 'Alright, that\'s 310. Let\'s get more custom messages at 480.'
                elif c == 480:
                    bump_score = 'Hello there! Did you know this is your 480th bump? That means your **minimal** wait time is 60 days. ' +\
                                 'And since I think you didn\'t really bump every three hours, that means you\'ve been here for a ' +\
                                 'looooooong time. _Please, tell me your secret._'
                elif c == 500:
                    bump_score = 'Hey, 500 bumps! Please go see Kody and tell him to give you a random Steam game!'
                elif c == 1000:
                    bump_score = 'Ayy 1000 bumps! Please go see Kody and tell him to shut me down (and to give you a steam game).'
                else:
                    bump_score = 'You bumped this server %s times.' % (str(c))

        await bot.send_message(message.channel, 'Thank you, %s! %s %s' % (last_bumper.mention, bump_score, random.choice(emojis)))

    # And now go to the bot commands
    await bot.process_commands(message)

    if len(message.attachments) > 0:
        try:
            save_path = conf.get('savepics', str(message.channel.id))  # get channel id who gets mod logs
            if save_path:
                for attach in message.attachments:
                    r = requests.get(attach['url'])
                    uniq_id = 5555555555 - int(time.time())
                    with open(save_path + str(uniq_id) + '_' + attach['filename'], 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:  # filter out keep-alive new chunks
                                f.write(chunk)
                                f.flush()
        except configparser.NoOptionError:
            pass


# On user join
@bot.event
async def on_member_join(member):
    server = member.server
    autoban = False
    muted = False

    # Check if it's not just an ad
    try:
        if any(x in member.name for x in banned_names):
            delete_content.append(member.id)
            await bot.ban(member, 7)
            autoban = True
    except:
        pass

    # Check if the user is in a ban list
    try:
        if False:  # not autoban:  DISABLING THIS FOR NOW
            check = checkBan(str(member.id))
            if len(check) > 0:
                # mute him if the server can do it
                muted = True
                muteid = conf.get('automute', str(server.id))  # get channel id who gets mod logs
                role = dutils.get(server.roles, id=muteid)
                await bot.add_roles(member, role)
    except:
        pass

    # Notify in defined channel for the server
    try:
        chan = conf.get('joinlogs', str(server.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # If there's nothing, don't do anything

    invite_code = 'a recently made invite'
    invite_user = 'someone, please check audit log'
    user_created = 'someday'

    try:
        curr_invites = {}
        sinv = await bot.invites_from(server)
        for invite in sinv:
            curr_invites[invite.code] = invite.uses

        for invite in invites[str(server.id)]:
            if invite.uses != curr_invites[invite.code]:
                invite_code = invite.code
                invite_user = '**' + invite.inviter.name + '**#' + invite.inviter.discriminator
    except:
        print('ERROR: Can\'t find the invite used for user join')

    try:
        if member.created_at is not None:
            user_created = "{} ({} UTC)".format(humanize.naturaltime(member.created_at + (datetime.now() - datetime.utcnow())),
                                                member.created_at)
    except:
        print('ERROR: Can\'t find the creation date for user join')

    # Build an embed
    if autoban:
        em = discord.Embed(title=member.name + '#' + member.discriminator + ' joined the server [WARNING]',
                           description='USER WILL BE BANNED AUTOMATICALLY. \n' +
                           member.mention + ' joined using ' + invite_code +
                           ' (created by ' + invite_user + ').\n' +
                           'Account was created ' + user_created,
                           colour=0x23D160, timestamp=datetime.utcnow())  # color: green
    elif muted:
        em = discord.Embed(title=member.name + '#' + member.discriminator + ' joined the server [WARNING]',
                           description='USER IS IN PUBLIC BANLIST. \n' +
                           member.mention + ' joined using ' + invite_code +
                           ' (created by ' + invite_user + ').\n' +
                           'Account was created ' + user_created,
                           colour=0x23D160, timestamp=datetime.utcnow())  # color: green
    else:
        em = discord.Embed(title=member.name + '#' + member.discriminator + ' joined the server',
                           description=member.mention + ' joined using ' + invite_code +
                           ' (created by ' + invite_user + ').\n' +
                           'Account was created ' + user_created,
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
        chan = conf.get('joinlogs', str(server.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # If there's nothing, don't do anything

    # Count for how long an user has been a member
    diff = relativedelta(datetime.utcnow(), member.joined_at)
    member_since = member.mention + ' was a member for %d months, %d days, %d hours, %d minutes and %d seconds.' % (
        diff.months, diff.days, diff.hours, diff.minutes, diff.seconds)

    # Build an embed
    em = discord.Embed(title=member.name + '#' + member.discriminator + ' left the server', description=member_since,
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
        chan = conf.get('joinlogs', str(server.id))  # get channel id who gets mod logs
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


# On message delete
@bot.event
async def on_message_delete(message):
    # Notify in defined channel for the server
    server = message.server
    author = message.author

    if server is None or author.discriminator == '0000' or str(message.type) != 'MessageType.default':
        return  # If there's nothing, don't do anything

    try:
        chan = conf.get('msglogs', str(server.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # Nothing to take care

    attch = []
    for a in message.attachments:
        attch.append(a['url'])

    # Build an embed
    em = discord.Embed(description=message.content + ' ' + ' '.join(attch),
                       colour=0x607D8B, timestamp=message.timestamp)  # color: dark grey
    em.set_author(name=author.name, icon_url=author.avatar_url)
    em.set_footer(text='#' + str(message.channel.name) + ' - ID: ' + str(message.id))

    if len(attch) > 0:
        em.set_image(url=attch[0])

    # Send message with embed
    await bot.send_message(discord.Object(int(chan)), 'Message deleted', embed=em)


# On message edit
@bot.event
async def on_message_edit(old, message):
    # Notify in defined channel for the server
    server = message.server
    author = message.author

    if server is None or author.discriminator == '0000' or str(message.type) != 'MessageType.default':
        return  # If there's nothing, don't do anything

    try:
        chan = conf.get('msglogs', str(server.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None or old.content == message.content:
        return  # Nothing to take care

    attch = []
    for a in message.attachments:
        attch.append(a['url'])

    # Build an embed
    em = discord.Embed(colour=0x800080, timestamp=message.timestamp)  # color: purple
    em.add_field(name='Before', inline=False, value=old.content + ' ' + ' '.join(attch))
    em.add_field(name='After', inline=False, value=message.content + ' ' + ' '.join(attch))
    em.set_author(name=author.name, icon_url=author.avatar_url)
    em.set_footer(text='#' + str(message.channel.name) + ' - ID: ' + str(message.id))

    # Send message with embed
    await bot.send_message(discord.Object(int(chan)), 'Message edited', embed=em)


# Update invite list
async def check_invites():
    await bot.wait_until_ready()
    ic = 0
    while not bot.is_closed:
        for server in bot.servers:
            try:
                ic += 1
                invites[server.id] = await bot.invites_from(server)
                if ic > 2:  # check three servers and wait 5 seconds
                    await asyncio.sleep(5)
                    ic = 0
            except:
                pass


# Delete old messages in temp channel
async def clean_temp():
    await bot.wait_until_ready()

    while not bot.is_closed:
        conf.read('./config.ini')  # re-read, in case we changed something
        channels = dict(conf.items('cleantemp'))

        for channel in channels:
            chan = bot.get_channel(channel)
            limit_date = datetime.utcnow() - timedelta(days=7)

            async for message in bot.logs_from(chan, before=limit_date, reverse=True):  # load logs older than 7 days
                try:
                    await bot.delete_message(message)
                    await asyncio.sleep(2)
                    # deleted = await bot.purge_from(chan, before=message)  # delete anything older than 7 days
                    # if len(deleted) > 0:  # log in console that it deleted stuff
                    #     print(str(channel) + ' deleted ' + str(len(deleted)) + ' messages')
                except Exception as e:
                    print(str(channel) + ' can\'t delete message there')
                    print(str(e))

                # break  # we only needed the first message in log, actually

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
            sqlite_version = data[0]
    except Exception as e:
        print("Error : " + str(e))
        exit(1)

    try:
        bot.loop.create_task(clean_temp())
        bot.loop.create_task(check_invites())
        bot.run(conf.get('bot', 'token'))
    except:
        exit(5)
