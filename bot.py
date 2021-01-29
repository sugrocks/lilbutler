import os
import time
import logging
import asyncio
import discord
import sqlite3
import requests
import humanize
import configparser
import better_exceptions

from shutil import copyfile
from botutils import is_mod
from datetime import datetime, timedelta
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
intents = discord.Intents.default()
intents.members = True
description = '"You people have too much money!"'
bot = commands.Bot(max_messages=15000, command_prefix='~', description=description, pm_help=True, intents=intents)

# init
better_exceptions.MAX_LENGTH = None
whitelisted_guilds = conf.get('bot', 'whitelist').split(',')
db = None
sqlite_version = '???'
invites = {}
banned_names = ['discord.gg', 'free games', 'discord.io', 'discord.me', 'invite.gg', 'twitch.tv', 'twitter.com']


# On bot login
@bot.event
async def on_ready():
    s = bot.guilds
    exitme = False
    for guild in s:
        try:
            if str(guild.id) not in whitelisted_guilds:
                print(guild.name + ' not in whitelist, leaving.')
                exitme = True
                await guild.leave()
        except:
            pass

    if exitme:
        bot.close()
        exit(0)

    print('/-----------------------------------------------------------------------------')
    print('| # ME')
    print('| Name:     ' + bot.user.name)
    print('| ID:       ' + str(bot.user.id))
    print('| Invite:   https://discord.now.sh/' + str(bot.user.id) + '?p1543892215')
    print('| SQLite:   ' + sqlite_version)
    print('|-----------------------------------------------------------------------------')
    print('| # MODULES')
    # Import our 'modules'
    bot.load_extension('utilities')
    bot.load_extension('mod')
    bot.load_extension('minesweeper')
    print('|-----------------------------------------------------------------------------')
    print('| # SERVERS (' + str(len(bot.guilds)) + ')')
    for guild in bot.guilds:
        print('| > Name:   ' + guild.name + ' (' + str(guild.id) + ')')
        if guild.me.nick:
            print('|   Nick:   ' + guild.me.nick)
    print('\\-----------------------------------------------------------------------------')


# On new messages
@bot.event
async def on_message(message):
    # Remove messages if they're in the blacklist
    blacklist = ['discord.gg', 'discordapp.com/invite']
    if any(thing in message.content for thing in blacklist) and not is_mod(message):
        await message.delete()
        return

    # And now go to the bot commands
    await bot.process_commands(message)

    if len(message.attachments) > 0:
        try:
            save_path = conf.get('savepics', str(message.channel.id))  # get where we save some pics
            if save_path:
                for attach in message.attachments:
                    r = requests.get(attach.url)
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
    guild = member.guild
    autoban = False

    # Check if it's not just an ad
    try:
        if any(x in member.name for x in banned_names):
            await member.guild.ban(member, delete_message_days=7, reason="Banned name")
            autoban = True
    except:
        pass

    # Notify in defined channel for the guild
    try:
        chan = conf.get('joinlogs', str(guild.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # If there's nothing, don't do anything

    invite_code = 'a recently made invite'
    invite_user = 'someone, please check audit log'
    user_created = 'someday'

    try:
        curr_invites = {}
        sinv = await guild.invites()
        for invite in sinv:
            curr_invites[invite.code] = invite.uses

        for invite in invites[str(guild.id)]:
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
        em = discord.Embed(title=member.name + '#' + member.discriminator + ' joined the guild [WARNING]',
                           description='USER WILL BE BANNED AUTOMATICALLY. \n' +
                           member.mention + ' joined using ' + invite_code +
                           ' (created by ' + invite_user + ').\n' +
                           'Account was created ' + user_created,
                           colour=0x23D160, timestamp=datetime.utcnow())  # color: green
    else:
        em = discord.Embed(title=member.name + '#' + member.discriminator + ' joined the guild',
                           description=member.mention + ' joined using ' + invite_code +
                           ' (created by ' + invite_user + ').\n' +
                           'Account was created ' + user_created,
                           colour=0x23D160, timestamp=datetime.utcnow())  # color: green
    em.set_thumbnail(url=member.avatar_url)
    em.set_footer(text='ID: ' + str(member.id))

    # Send message with embed
    await bot.get_channel(int(chan)).send(embed=em)


# On user leave
@bot.event
async def on_member_remove(member):
    # Notify in defined channel for the guild
    guild = member.guild

    try:
        chan = conf.get('joinlogs', str(guild.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # If there's nothing, don't do anything

    # Count for how long an user has been a member
    diff = relativedelta(datetime.utcnow(), member.joined_at)
    member_since = member.mention + ' was a member for %d months, %d days, %d hours, %d minutes and %d seconds.' % (
        diff.months, diff.days, diff.hours, diff.minutes, diff.seconds)

    # Build an embed
    em = discord.Embed(title=member.name + '#' + member.discriminator + ' left the guild', description=member_since,
                       colour=0xE81010, timestamp=datetime.utcnow())  # color: red
    em.set_thumbnail(url=member.avatar_url)
    em.set_footer(text='ID: ' + str(member.id))

    # Send message with embed
    await bot.get_channel(int(chan)).send(embed=em)


# On user ban
@bot.event
async def on_member_ban(member):
    # Notify in defined channel for the guild
    guild = member.guild

    try:
        chan = conf.get('joinlogs', str(guild.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # If there's nothing, don't do anything

    # Build an embed
    em = discord.Embed(title=member.name + ' is now banned from the guild',
                       colour=0x7289DA, timestamp=datetime.utcnow())  # color: blue
    em.set_thumbnail(url=member.avatar_url)
    em.set_footer(text='ID: ' + str(member.id))

    # Send message with embed
    await bot.get_channel(int(chan)).send(embed=em)


# On message delete
@bot.event
async def on_message_delete(message):
    # Notify in defined channel for the guild
    guild = message.guild
    author = message.author

    if guild is None or author.discriminator == '0000' or message.type != discord.MessageType.default:
        return  # If there's nothing, don't do anything

    try:
        chan = conf.get('msglogs', str(guild.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # Nothing to take care

    attch = []
    for a in message.attachments:
        attch.append(a.url)

    # Build an embed
    em = discord.Embed(description=message.content + ' ' + ' '.join(attch),
                       colour=0x607D8B, timestamp=message.created_at)  # color: dark grey
    em.set_author(name=author.name, icon_url=author.avatar_url)
    em.set_footer(text='#' + str(message.channel.name) + ' - ID: ' + str(message.id))

    if len(attch) > 0:
        em.set_image(url=attch[0])

    # Send message with embed
    await bot.get_channel(int(chan)).send('Message deleted', embed=em)


# On message edit
@bot.event
async def on_message_edit(old, message):
    # Notify in defined channel for the guild
    guild = message.guild
    author = message.author

    if guild is None or author.discriminator == '0000' or message.type != discord.MessageType.default:
        return  # If there's nothing, don't do anything

    try:
        chan = conf.get('msglogs', str(guild.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None or old.content == message.content:
        return  # Nothing to take care

    attch = []
    for a in message.attachments:
        attch.append(a.url)

    # Build an embed
    em = discord.Embed(colour=0x800080, timestamp=message.created_at)  # color: purple
    em.add_field(name='Before', inline=False, value=old.content + ' ' + ' '.join(attch))
    em.add_field(name='After', inline=False, value=message.content + ' ' + ' '.join(attch))
    em.set_author(name=author.name, icon_url=author.avatar_url)
    em.set_footer(text='#' + str(message.channel.name) + ' - ID: ' + str(message.id))

    # Send message with embed
    await bot.get_channel(int(chan)).send('Message edited', embed=em)


# Update invite list
async def check_invites():
    await bot.wait_until_ready()
    ic = 0
    while not bot.is_closed:
        for guild in bot.guilds:
            try:
                ic += 1
                invites[str(guild.id)] = await guild.invites()
                if ic > 2:  # check three guilds and wait 5 seconds
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

            async for message in chan.history(before=limit_date, oldest_first=True):  # load logs older than 7 days
                try:
                    await message.delete()
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
