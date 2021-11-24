import os
import re
import logging
import asyncio
import discord
import sqlite3
import configparser
import better_exceptions

from shutil import copyfile
from botutils import is_mod
from discord.ext import commands
from datetime import datetime, timedelta
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
bot = commands.Bot(
    max_messages=15000,
    command_prefix=commands.when_mentioned_or('lil!'),
    description='"You people have too much money!"',
    help_command=None,
    intents=intents
)

commands = [
    discord.ApplicationCommand(
        name="sleep",
        description="Stop the bot, might come back automatically."
    ),
    discord.ApplicationCommand(
        name="clean",
        description="Delete my own messages."
    ),
    discord.ApplicationCommand(
        name="ping",
        description="PONG!"
    ),
    discord.ApplicationCommand(
        name="birthday",
        description="Toggle the birthday role, if available.",
        options=[discord.ApplicationCommandOption(
            name="user",
            description="The targeted user",
            type=discord.ApplicationCommandOptionType.user,
            required=True
        )]
    ),
    discord.ApplicationCommand(
        name="cn",
        description="Get Cartoon Network's schedule",
        options=[discord.ApplicationCommandOption(
            name="date",
            description="Type a date in the YYYY-MM-DD format.",
            type=discord.ApplicationCommandOptionType.string,
            required=True
        )]
    ),
    discord.ApplicationCommand(
        name="howlong",
        description="Get when someone joined the server.",
        options=[discord.ApplicationCommandOption(
            name="user",
            description="The targeted user",
            type=discord.ApplicationCommandOptionType.user,
            required=False
        )]
    ),
    discord.ApplicationCommand(
        name="pick",
        description="Pick an element in a list",
        options=[discord.ApplicationCommandOption(
            name="list",
            description="Type multiple choices, delimited by a comma.",
            type=discord.ApplicationCommandOptionType.string,
            required=True
        )]
    ),
    discord.ApplicationCommand(
        name="nuke",
        description="Delete a number of messages.",
        options=[discord.ApplicationCommandOption(
            name="count",
            description="Number of messages to delete (defaults to 50).",
            type=discord.ApplicationCommandOptionType.number,
            required=False
        )]
    )
]

# init
better_exceptions.MAX_LENGTH = None
whitelisted_guilds = conf.get('bot', 'whitelist').split(',')
db = None
sqlite_version = '???'
invites = {}
banned_names = ['free games', 'discord .', 'discord.', 'invite.gg', 'twitch.', 'twitter.', 'twitter .', 'twitter dot']
social_galleries = ['twitter.com', 'pixiv.net', 'imgur.com', 'reddit.com', 'redgifs.com']


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
    print('| Invite:   https://discord.com/oauth2/authorize?client_id=' + str(bot.user.id) +
          '&permissions=397553298678&scope=applications.commands%20bot')
    print('| SQLite:   ' + sqlite_version)
    print('|-----------------------------------------------------------------------------')
    print('| # MODULES')
    # Import our 'modules'
    bot.load_extension('utilities')
    bot.load_extension('mod')
    print('|-----------------------------------------------------------------------------')
    print('| # SERVERS (' + str(len(bot.guilds)) + ')')
    for guild in bot.guilds:
        print('| > Name:   ' + guild.name + ' (' + str(guild.id) + ')')
        print('|   Registering commands...')
        await bot.register_application_commands(commands, guild=guild)
        if guild.me.nick:
            print('|   Nick:   ' + guild.me.nick)
    print('\\-----------------------------------------------------------------------------')


# On new messages
@bot.event
async def on_message(message):
    # Remove messages if they're in the blacklist
    blacklist = ['discord.gg', 'discordapp.com/invite']
    if any(thing in message.content for thing in blacklist) and not is_mod(message.channel, message.author):
        await message.delete()
        return

    # And now go to the bot commands
    await bot.process_commands(message)

    if len(message.attachments) > 0:
        try:
            save_path = conf.get('savepics', str(message.channel.id))  # get where we save some pics
            if save_path:
                for attach in message.attachments:
                    uniq_id = 5555555555 - int(datetime.timestamp(message.created_at))
                    await attach.save(save_path + str(uniq_id) + '_' + attach.filename)
        except configparser.NoOptionError:
            pass

    # To save URLs for third party services where we should archive media
    if any(thing in message.content for thing in social_galleries):
        save_path = conf.get('savepics', str(message.channel.id))  # get where we save some pics
        if save_path:
            matches = re.finditer(r"(https?://[^\s]+)", message.content)
            for _, match in enumerate(matches):
                url = match.group()
                # One more time
                if any(thing in url for thing in social_galleries):
                    with open(save_path + 'todl.txt', 'a+') as f:
                        f.write(url + '\n')


# On user join
@bot.event
async def on_member_join(member):
    guild = member.guild
    autoban = False

    # Check if it's not just an ad
    try:
        if any(x in member.name.lower() for x in banned_names):
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

    user_created = '???'

    try:
        if member.created_at is not None:
            user_created = '<t:' + str(int(member.created_at.timestamp())) + ':R>'
    except:
        print('ERROR: Can\'t find the creation date for user join')

    # Build an embed
    if autoban:
        em = discord.Embed(title=member.name + '#' + member.discriminator + ' joined the server [WARNING]',
                           description='USER WILL BE BANNED AUTOMATICALLY. \n' +
                           member.mention + ' joined.\n' +
                           'Account was created ' + user_created,
                           colour=0x23D160,  # color: green
                           timestamp=datetime.utcnow())
    else:
        em = discord.Embed(title=member.name + '#' + member.discriminator + ' joined the server',
                           description=member.mention + ' joined.\n' +
                           'Account was created ' + user_created,
                           colour=0x23D160,  # color: green
                           timestamp=datetime.utcnow())
    em.set_thumbnail(url=member.display_avatar.url)
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
    diff = relativedelta(datetime.utcnow(), member.joined_at.replace(tzinfo=None))
    member_since = member.mention + ' was a member for '
    if diff.years > 0:
        member_since += str(diff.years) + ' year' + ('s ' if diff.years != 1 else ' ')
    if diff.months > 0:
        member_since += str(diff.months) + ' month' + ('s ' if diff.months != 1 else ' ')
    if diff.days > 0:
        member_since += str(diff.days) + ' day' + ('s ' if diff.days != 1 else ' ')
    if diff.hours > 0:
        member_since += str(diff.hours) + ' hour' + ('s ' if diff.hours != 1 else ' ')
    member_since += str(diff.minutes) + ' minute' + ('s and ' if diff.minutes != 1 else ' and ')
    member_since += str(diff.seconds) + ' second' + ('s.' if diff.seconds != 1 else '.')

    # Build an embed
    em = discord.Embed(title=member.name + '#' + member.discriminator + ' left the server',
                       description=member_since,
                       colour=0xE81010,  # color: red
                       timestamp=datetime.utcnow())
    em.set_thumbnail(url=member.display_avatar.url)
    em.set_footer(text='ID: ' + str(member.id))

    # Send message with embed
    await bot.get_channel(int(chan)).send(embed=em)


# On user ban
@bot.event
async def on_member_ban(guild, member):
    try:
        chan = conf.get('joinlogs', str(guild.id))  # get channel id who gets mod logs
    except configparser.NoOptionError:
        return

    if chan is None:
        return  # If there's nothing, don't do anything

    # Build an embed
    em = discord.Embed(title=member.name + ' is now banned from the server',
                       colour=0x7289DA,  # color: blue
                       timestamp=datetime.utcnow())
    em.set_thumbnail(url=member.display_avatar.url)
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
                       colour=0x607D8B,  # color: dark grey
                       timestamp=message.created_at)
    em.set_author(name=author.name, icon_url=author.display_avatar.url)
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
    em.set_author(name=author.name, icon_url=author.display_avatar.url)
    em.set_footer(text='#' + str(message.channel.name) + ' - ID: ' + str(message.id))

    # Send message with embed
    await bot.get_channel(int(chan)).send('Message edited', embed=em)


# Delete old messages in temp channel
async def clean_temp():
    await bot.wait_until_ready()

    while not bot.is_closed():
        conf.read('./config.ini')  # re-read, in case we changed something
        channels = dict(conf.items('cleantemp'))

        for channel in channels:
            chan = bot.get_channel(int(channel))
            limit_date = datetime.now() - timedelta(days=7)

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

        await asyncio.sleep(60 * 5)  # sleep 15 minutes


async def main():
    await bot.login(conf.get('bot', 'token'))
    bot.loop.create_task(clean_temp())
    await bot.register_application_commands(None)  # Clear commands
    await bot.connect()


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
        loop = bot.loop
        loop.run_until_complete(main())
    except:
        exit(5)
