import configparser
from discord.ext import commands

# Setup config
conf = configparser.ConfigParser()
conf.read('./config.ini')

# Setup discord-stuff
description = '"ignore me pls"'
bot = commands.Bot(command_prefix='lilR!', description=description)


# On bot login
@bot.event
async def on_ready():
    for guild in bot.guilds:
        roles = guild.roles
        clist = []

        for r in roles:
            if r.colour.to_rgb() != (0, 0, 0):  # Roles without colors are not dumped
                clist.append({
                    'id': r.position,
                    'r': r.colour.r,
                    'g': r.colour.g,
                    'b': r.colour.b,
                    'snowflake': r.id,
                    'name': r.name
                })

        # Order list
        slist = sorted(clist, key=lambda x: x['id'], reverse=True)

        # Print list
        print('\n\n=== %s ===' % guild.name)

        for rl in slist:
            print('%s (%s) - #%02x%02x%02x' %
                  (rl['name'], rl['snowflake'], rl['r'], rl['g'], rl['b']))

    print('\n\nDone!')


# Launch
bot.run(conf.get('bot', 'token'))
