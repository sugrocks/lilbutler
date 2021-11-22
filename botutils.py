# Helpers
import discord


def is_admin(channel, author):
    return channel.permissions_for(author).administrator


def is_mod(channel, author):
    return channel.permissions_for(author).kick_members


async def reply(ctx, message, *, ephemeral: bool = False):
    if isinstance(ctx, discord.ext.commands.context.SlashContext):
        return await ctx.send(message, ephemeral=ephemeral)
    else:
        delete_after = None
        if ephemeral:
            delete_after = 5.0
            await ctx.message.delete(delay=delete_after)

        return await ctx.reply(message, delete_after=delete_after)
