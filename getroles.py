import configparser
from discord.ext import commands

# Setup config
conf = configparser.ConfigParser()
conf.read('./config.ini')

# Setup discord-stuff
description = '"ignore me pls"'
bot = commands.Bot(command_prefix='!!!!!', description=description)


# On bot login
@bot.event
async def on_ready():
    for server in bot.servers:
        roles = server.roles
        clist = []

        for r in roles:
            if r.colour.to_tuple() != (0, 0, 0):  # Roles without colors are not dumped
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
        print('\n\n=== %s ===' % server.name)

        for l in slist:
            print('%s (%s) - #%02x%02x%02x' %
                  (l['name'], l['snowflake'], l['r'], l['g'], l['b']))


# Launch
bot.run(conf.get('bot', 'token'))
