import discord
import configparser

from discord.ext import commands
from botutils import del_message, is_mod
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_commands


class Mod(commands.Cog):
    """Commands for mods."""
    def __init__(self, bot):
        self.bot = bot
        self.conf = configparser.ConfigParser()
        self.conf.read('./config.ini')
        print('| Loaded:   mod')

    def is_me(self, message):
        return message.author == self.bot.user

    # @commands.command(description='Toggle the birthday role, if available.')
    @cog_ext.cog_slash(
        name="birthday",
        description="Toggle the birthday role, if available.",
        options=[manage_commands.create_option(
            name="user",
            description="The targeted user",
            option_type=6,
            required=True
        )],
        guild_ids=[217111753614426112, 274151655795064832]
    )
    async def _birthday(self, ctx: SlashContext, user: discord.Member=None):
        """Happy Birthday!"""
        await ctx.respond(eat=True)

        if not is_mod(ctx.channel, ctx.author):
            await ctx.send('Sorry but you\'re not allowed to do that.', hidden=True)
            return

        # Quit if no user mentioned or no id
        if user is None:
            await ctx.send('I need to know who needs to get their roles changed.', hidden=True)
            return

        try:
            # await ctx.trigger_typing()
            user_roles = user.roles

            # Remove role (if found in user) and return
            for r in user.roles:
                if str(r.id) == self.conf.get('birthday', str(ctx.guild.id)):
                    user_roles.remove(r)
                    await user.edit(roles=user_roles)
                    await ctx.send('Birthday time is over.', hidden=True)
                    return

            # Add role and return
            for r in user.guild.roles:
                if str(r.id) == self.conf.get('birthday', str(ctx.guild.id)):
                    user_roles.append(r)
                    await user.edit(roles=user_roles)
                    await ctx.send('Happy birthday %s!' % user.mention)
                    return

        except Exception as e:
            print('>>> ERROR birthday ', e)

    @commands.command(description='But I might come back!')
    async def sleep(self, ctx):
        """Stops the bot."""
        if str(ctx.message.author.id) != self.conf.get('bot', 'owner_id'):
            await ctx.reply('Sorry but you\'re not allowed to do that.')
            return

        await del_message(self, ctx)
        exit(0)  # I guess it crashes the app too, but whatever

    @commands.command(description='In case I went crazy...')
    async def clean(self, ctx):
        """Delete my own messages."""
        if not is_mod(ctx.message.channel, ctx.message.author):
            await ctx.reply('Sorry but you\'re not allowed to do that.')
            return

        try:
            await ctx.trigger_typing()
            deleted = await ctx.message.channel.purge(before=ctx.message, limit=1000, check=self.is_me)
            if len(deleted) > 2:
                await ctx.send('Deleted %d of my own messages.' % len(deleted))
            await del_message(self, ctx)
        except Exception as e:
            print('>>> ERROR clean ', e)

    @commands.command(description='Specify a number or I will clean the last 50 messages.')
    async def nuke(self, ctx, nbr: int = 50):
        """Delete a number of messages."""
        if not is_mod(ctx.message.channel, ctx.message.author):
            await ctx.reply('Sorry but you\'re not allowed to do that.')
            return

        try:
            await ctx.trigger_typing()
            deleted = await ctx.message.channel.purge(before=ctx.message, limit=nbr)
            if len(deleted) > 2:
                await ctx.send('Deleted %d messages.' % len(deleted))
            await del_message(self, ctx)
        except Exception as e:
            print('>>> ERROR clean ', e)


def setup(bot):
    bot.add_cog(Mod(bot))
