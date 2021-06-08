import discord
import configparser
import better_exceptions

from datetime import datetime

# Setup config
conf = configparser.ConfigParser()
conf.read('./config.ini')

# init
better_exceptions.MAX_LENGTH = None

# Setup discord-stuff
class MyClient(discord.Client):
    async def on_ready(self):
        print('Hi')

        chanid = 242477869559840768
        messid = 842375286209511470

        chan = await self.fetch_channel(chanid)
        mess = await chan.fetch_message(messid)

        for reaction in mess.reactions:
            async for user in reaction.users():
                member = await chan.guild.fetch_member(user.id)
                str = member.name + '#' + member.discriminator
                if member.nick:
                    str += ' (' + member.nick + ')'

                print(str)


        print('Done!')
        exit(0)

client = MyClient()
client.run(conf.get('bot', 'token'))
