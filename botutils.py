import asyncio


# Helpers
def is_admin(ctx):
    return ctx.message.channel.permissions_for(ctx.message.author).administrator


def is_mod(ctx):
    return ctx.message.channel.permissions_for(ctx.message.author).kick_members


async def del_message(self, ctx):
    if ctx.message.server:
        await self.bot.delete_message(ctx.message)
