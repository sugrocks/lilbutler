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

        a = datetime(2021, 1, 30, 13, 40, 0)
        b = datetime(2022, 1, 30, 13, 30, 0)
        channels = [304390046260396034, 350380450528886784]
        for c in channels:
            channel = self.get_channel(c)
            print('Starting for channel ' + str(channel.name))
            i = 0
            async for message in channel.history(limit=None, before=b, after=a):
                if i % 50 == 0:
                    print('Messages parsed: ' + str(i))

                i += 1

                if len(message.attachments) > 0:
                    try:
                        save_path = conf.get('savepics', str(message.channel.id))  # get where we save some pics
                        if save_path:
                            for attach in message.attachments:
                                uniq_id = 5555555555 - int(datetime.timestamp(message.created_at))
                                await attach.save(save_path + str(uniq_id) + '_' + attach.filename)
                    except configparser.NoOptionError:
                        print('No save path?')
                        pass

        print('Done!')


client = MyClient()
client.run(conf.get('bot', 'token'))
