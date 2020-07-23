# Helpers
def is_admin(message):
    return message.channel.permissions_for(message.author).administrator


def is_mod(message):
    return message.channel.permissions_for(message.author).kick_members


async def del_message(self, ctx):
    if ctx.guild:
        await ctx.message.delete()
