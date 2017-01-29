import logging
import asyncio
import configparser
from botutils import is_mod
from discord.ext import commands

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
bot = commands.Bot(command_prefix='!', description=description)


# On bot login
@bot.event
async def on_ready():
    print('I\'m ' + bot.user.name + '!')
    print('ID: ' + bot.user.id)
    print('------------------')
    # Import our 'modules'
    bot.load_extension('utilities')
    bot.load_extension('mod')


@bot.event
async def on_message(message):
    blacklist = ['discord.gg', 'discordapp.com/invite']
    if any(thing in message.content for thing in blacklist) and not is_mod(message):
        await bot.delete_message(message)
        return

    await bot.process_commands(message)


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
    bot.loop.create_task(clean_temp())
    bot.run(conf.get('bot', 'token'))
