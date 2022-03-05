"""
Code a discord bot to keep servers clean.
A bot to help keep Discord servers clean from profanity. Bot will search messages sent to channels for profanity, deleting profane text and timeout user for 5 min , logs banned users to a special channel.
Bot will also automatically give users muted role on their 5th offense.
Add a slash-command that would add or remove profanity from the filter, you may edit the en.txt file. To remove a word or phrase, delete it from the file; to add, add the new word or phrase on a new line.
"""
import json
import re
from datetime import datetime, timedelta, timezone
import logging
import hikari
import lightbulb
import os

logging.basicConfig(level=logging.INFO, filename='log.log', filemode='w',
                    format='%(asctime)s - %(name)-5s - %(levelname)5s - %(message)s',
                    datefmt='%m-%d %H:%M')

filter_logger = logging.getLogger("Filter-list-Log")

bot = lightbulb.BotApp(os.environ['TOKEN'], prefix='=')


@bot.listen(hikari.StartedEvent)
async def on_started(event):
    print(f'=====\nLogged in as {bot.get_me().username} | {bot.get_me().id}\n=====')


@bot.listen(hikari.GuildMessageCreateEvent)
async def on_guild_message_create(event):
    msg_create = logging.getLogger("Message_Create")
    if event.author.is_system or event.author.is_bot or (
            hikari.Permissions.ADMINISTRATOR in lightbulb.utils.permissions.permissions_for(event.member)
    ):
        return
    with open('en.txt', 'r', encoding='utf-8') as f:
        profanity = f.read().strip('\ufeff').splitlines()
    pd = []
    for word in profanity:
        w = r'\b' + word + r'+\b'
        if re.search(w, event.message.content.lower()):
            pd.append(word)
    if len(pd) == 0:
        return
    await event.message.delete()
    channel = await event.message.fetch_channel()
    embed = hikari.Embed(title='Profanity detected',
                         description=f'{event.author.mention}, you have been muted for 5 minutes.',
                         color=0xFF0000)
    embed.timestamp = event.message.created_at
    await channel.send(embed=embed)

    await event.member.edit(communication_disabled_until=datetime.now(timezone.utc) + timedelta(minutes=5))

    # Logging

    msg_create.warning(
        f'{event.author.username}#{event.author.discriminator} ({event.author.id}) received a timeout for 5 '
        f'minutes.')

    embed = hikari.Embed(title=f'Mute',
                         description=f'{event.author.mention} received a timeout of 5 minutes. \nReason: '
                                     f'Profanity detected.',
                         color=0xFF0000)
    embed.timestamp = event.message.created_at
    embed.add_field(name='Message:', value=f"**in <#{event.channel_id}>**\n> {event.message.content}")
    embed.add_field(name='Word(s) detected:', value=f"||{pd}||")
    await bot.cache.get_guild_channel(
        json.load(open('config.json', 'r'))['logging_channel'][str(event.guild_id)]).send(embed=embed)
    log_file = json.load(open('warn_count.json', 'r'))
    log_file[str(event.author.id)] = log_file.get(str(event.author.id), 0) + 1
    json.dump(log_file, open('warn_count.json', 'w'), indent=4)
    if log_file[str(event.author.id)] >= 5:
        config = json.load(open('config.json', 'r'))
        msg_create.info(f'{event.author.username}#{event.author.discriminator} ({event.author.id}) received a '
                        f'Muted role ({config["muted_role"][str(event.guild_id)]})')
        await event.member.edit(roles=[config["muted_role"][str(event.guild_id)]])
        embed = hikari.Embed(title='Profanity Offense',
                             description=f'{event.author.mention} has been given <@&{config["muted_role"][str(event.guild_id)]}> for '
                                         f'their 6th profanity '
                                         f'offense.',
                             color=0xFF0000)
        embed.set_author(name=f"{event.message.author.username}#{event.message.author.discriminator}")
        embed.timestamp = event.message.created_at

        await bot.cache.get_guild_channel(
            json.load(open('config.json', 'r'))['logging_channel'][str(event.guild_id)]).send(embed=embed)
        log_file[str(event.author.id)] = 0
        json.dump(log_file, open('warn_count.json', 'w'), indent=4)
    return


@bot.listen(hikari.GuildMessageUpdateEvent)
async def on_guild_message_update(event):
    msg_update = logging.getLogger("Message_Update")
    if event.author.is_system or event.author.is_bot or (
            hikari.Permissions.ADMINISTRATOR in lightbulb.utils.permissions.permissions_for(event.member)
    ):
        return
    with open('en.txt', 'r') as f:
        profanity = f.read().splitlines()
    pd = []
    for word in profanity:
        w = r'\b' + word + r'+\b'
        if re.search(w, event.message.content.lower()):
            pd.append(word)
    if len(pd) == 0:
        return
    await event.message.delete()
    embed = hikari.Embed(title='Profanity detected',
                         description=f'{event.author.mention}, you have been muted for 5 minutes.',
                         color=0xFF0000)
    embed.timestamp = event.message.created_at
    channel = await event.message.fetch_channel()
    await channel.send(embed=embed)
    await event.member.edit(communication_disabled_until=datetime.now(timezone.utc) + timedelta(minutes=5))

    # Logging
    msg_update.warning(
        f'{event.author.username}#{event.author.discriminator} ({event.author.id}) received a timeout for 5 '
        f'minutes.')

    embed = hikari.Embed(title=f'Mute',
                         description=f'{event.author.mention} received a timeout of 5 minutes. \nReason: '
                                     f'Profanity detected.',
                         color=0xFF0000)
    embed.timestamp = event.message.created_at
    embed.add_field(name='Message:', value=f"**in <#{event.channel_id}>**\n> {event.message.content}")
    embed.add_field(name='Word(s) detected:', value=f"||{pd}||")
    await bot.cache.get_guild_channel(
        json.load(open('config.json', 'r'))['logging_channel'][str(event.guild_id)]).send(embed=embed)
    log_file = json.load(open('warn_count.json', 'r'))
    log_file[str(event.author.id)] = log_file.get(str(event.author.id), 0) + 1
    json.dump(log_file, open('warn_count.json', 'w'), indent=4)
    if log_file[str(event.author.id)] >= 5:
        config = json.load(open('config.json', 'r'))
        msg_update.info(f'{event.author.username}#{event.author.discriminator} ({event.author.id}) received a '
                        f'Muted role ({config["muted_role"][str(event.guild_id)]})')
        await event.member.edit(roles=[config["muted_role"][str(event.guild_id)]])
        embed = hikari.Embed(title='Profanity Offense',
                             description=f'{event.author.mention} has been given <@&{config["muted_role"][str(event.guild_id)]}> for '
                                         f'their 6th profanity '
                                         f'offense.',
                             color=0xFF0000)
        embed.set_author(name=f"{event.message.author.username}#{event.message.author.discriminator}")
        embed.timestamp = event.message.created_at

        await bot.cache.get_guild_channel(
            json.load(open('config.json', 'r'))['logging_channel'][str(event.guild_id)]).send(embed=embed)
        log_file[str(event.author.id)] = 0
        json.dump(log_file, open('warn_count.json', 'w'), indent=4)
    return


@bot.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command(name="filter", description="Filter a word from the server.")
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def msg_filter(ctx):
    pass


@msg_filter.child
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("word", "Word to ban", str, required=True)
@lightbulb.command("add", "Adds a word to the filter list.")
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def add_filter(ctx: lightbulb.Context) -> None:
    with open('en.txt', 'r') as f:
        profanity = f.read().splitlines()
    if ctx.options.word.lower() in profanity:
        await ctx.respond(f'{ctx.author.mention}, that word is already in the filter list.')
        return
    with open('en.txt', 'a') as f:
        f.write(f'{ctx.options.word.lower()}\n')
        e = hikari.Embed(title='Word added to filter list',
                         description=f'{ctx.author.mention}, ||{ctx.options.word.lower()}|| has been added to the '
                                     f'filter list.',
                         color=hikari.Color.from_hex_code('#57F287'))
        e.timestamp = datetime.now(timezone.utc)
        await ctx.respond(embed=e)
        filter_logger.info(
            f'{ctx.author.username}#{ctx.author.discriminator} removed `{ctx.options.word.lower()}` from the filter '
            f'list.')


@msg_filter.child
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option('word', 'string to ban', type=str, required=True)
@lightbulb.command('remove', 'Remove a word from the filter list.')
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def remove_filter(ctx):
    with open('en.txt', 'r') as f:
        profanity = f.read().splitlines()
    if ctx.options.word.lower() not in profanity:
        await ctx.respond(f'{ctx.author.mention}, that word is not in the filter list.')
        return
    with open('en.txt', 'r') as f:
        profanity = f.read().splitlines()
    with open('en.txt', 'w') as f:
        for word in profanity:
            if word != ctx.options.word.lower():
                f.write(f'{word}\n')
    e = hikari.Embed(title='Word removed from filter list',
                     description=f'{ctx.author.mention}, ||{ctx.options.word.lower()}|| has been removed from the '
                                 f'filter '
                                 f'list.',
                     color=hikari.Color.from_hex_code('#FEE75C'))
    e.timestamp = datetime.now(timezone.utc)
    await ctx.respond(embed=e)
    filter_logger.info(f'{ctx.author.username}#{ctx.author.discriminator} removed `{ctx.options.word.lower()}` from '
                       f'the filter list.')


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(
            f"Something went wrong during invocation of command `{event.context.command.name}`.")
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("You are not the owner of this bot.")
    elif isinstance(exception, lightbulb.MissingRequiredPermission):
        pass
    elif ...:
        ...
    else:
        raise exception


@bot.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option('member', 'Of whom?', type=hikari.Member, required=True)
@lightbulb.command('reset_warn_count', 'Resets warn counts for a user', aliases=["rwc"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def reset_warn_count(ctx):
    if ctx.options.member.id == ctx.author.id:
        await ctx.respond(f'{ctx.author.mention}, you can\'t reset your own warn count.')
        return
    if ctx.options.member.is_bot or (
            hikari.Permissions.ADMINISTRATOR in lightbulb.utils.permissions.permissions_for(ctx.options.member)):
        await ctx.respond(f'{ctx.author.mention}, {ctx.options.member.mention} can\'t have warnings.')
        return
    warn_counts = json.load(open('warn_count.json', 'r'))
    if str(ctx.options.member.id) in warn_counts:
        del warn_counts[str(ctx.options.member.id)]
        await ctx.respond(f'{ctx.author.mention}, the warn count for {ctx.options.member.mention} has been reset.')
    else:
        await ctx.respond(f'{ctx.author.mention}, {ctx.options.member.mention} has no warnings.')
    json.dump(warn_counts, open('warn_count.json', 'w'), indent=4)


@bot.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option('member', 'Of whom?', type=hikari.Member, required=True)
@lightbulb.command('warn_count', 'Show warn counts for a user', aliases=["wc"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def warn_count(ctx):
    if ctx.options.member.id == ctx.author.id:
        await ctx.respond(f'{ctx.author.mention}, you can\'t check your own warn count.')
        return
    if ctx.options.member.is_bot or (
            hikari.Permissions.ADMINISTRATOR in lightbulb.utils.permissions.permissions_for(ctx.options.member)):
        await ctx.respond(f'{ctx.author.mention}, {ctx.options.member.mention} can\'t have warnings.')
        return
    warn_counts = json.load(open('warn_count.json', 'r'))
    if not str(ctx.options.member.id) in warn_counts:
        color = hikari.Color.from_hex_code('#57F287')
    elif 0 < warn_counts[str(ctx.options.member.id)] < 4:
        color = hikari.Color.from_hex_code('#FEE75C')
    else:
        color = hikari.Color.from_hex_code('#ED4245')
    embed = hikari.Embed(title=f'Warn count(s)',
                         description=f'{ctx.options.member.mention} has {warn_counts.get(str(ctx.options.member.id), "no")}'
                                     f' warning(s).',
                         color=color)
    embed.timestamp = datetime.now(timezone.utc)
    await ctx.respond(embed=embed)


bot.run()
