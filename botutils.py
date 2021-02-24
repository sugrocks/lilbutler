# Helpers
def is_admin(channel, author):
    return channel.permissions_for(author).administrator


def is_mod(channel, author):
    return channel.permissions_for(author).kick_members


async def del_message(self, ctx):
    if ctx.guild:
        await ctx.message.delete()
