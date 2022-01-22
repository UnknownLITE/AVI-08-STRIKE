"""
Code a discord bot to keep servers clean.

A bot to help keep Discord servers clean from profanity. Bot will search messages sent to channels for profanity, deleting profane text and timeout user for 5 min , logs banned users to a special channel.

Bot will also automatically give users muted role (id: 933699268257144872) on their 5th offense.

Add a slashcommand that would add or remove profanity from the filter, you may edit the en.txt file. To remove a word or phrase, delete it from the file; to add, add the new word or phrase on a new line.
"""
import json
import re
from datetime import datetime, timedelta, timezone
from email.policy import default

import hikari
import lightbulb
import os

bot = lightbulb.BotApp(os.environ['TOKEN'],
                       default_enabled_guilds=834693207186341889)  # OTMzMjUzNDgwNDEwMzkwNTk4.Yee2CA.2p8QfaQAy24DRqF6IyRxWd5FRoM


@bot.listen(hikari.StartedEvent)
async def on_started(event):
    print(f'Logged in !!')


@bot.listen(hikari.GuildMessageCreateEvent)
async def on_guild_message_create(event):
    print(event.author, event.author.is_bot)
    if event.author.is_bot and not (
            hikari.Permissions.ADMINISTRATOR in lightbulb.utils.permissions.permissions_for(event.member)):
        return
    with open('en.txt', 'r', encoding='utf-8') as f:
        profanity = f.read().strip('\ufeff').splitlines()
    for word in profanity:
        word = r'\b' + word + r'\b'
        if re.search(word, event.message.content.lower()):
            channel = await event.message.fetch_channel()
            await event.message.delete()
            embed = hikari.Embed(title='Profanity detected',
                                 description=f'{event.author.mention}, you have been muted for 5 minutes.',
                                 color=0xFF0000)
            embed.timestamp = event.message.created_at
            await channel.send(embed=embed)

            await event.member.edit(communication_disabled_until=datetime.now(timezone.utc) + timedelta(minutes=5))

            # Logging
            embed = hikari.Embed(title=f'Mute',
                                 description=f'{event.author.mention} received a timeout of 5 minutes. \nReason: '
                                             f'Profanity detected.',
                                 color=0xFF0000)
            embed.timestamp = event.message.created_at
            embed.add_field(name='Message--', value=f"**in <#{event.channel_id}>**\n> {event.message.content}")
            await bot.cache.get_guild_channel(
                json.load(open('config.json', 'r'))['logging_channel'][str(event.guild_id)]).send(embed=embed)
            log_file = json.load(open('warn_count.json', 'r'))
            log_file[str(event.author.id)] = log_file.get(str(event.author.id), 0) + 1
            json.dump(log_file, open('warn_count.json', 'w'), indent=4)
            if log_file[str(event.author.id)] >= 5:
                config = json.load(open('config.json', 'r'))
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
    if event.author.is_bot and not (
            hikari.Permissions.ADMINISTRATOR in lightbulb.utils.permissions.permissions_for(event.member)):
        return
    with open('en.txt', 'r') as f:
        profanity = f.read().splitlines()
    for word in profanity:
        word = r'\b' + word + r'\b'
        if re.search(word, event.message.content.lower()):
            channel = await event.message.fetch_channel()
            await event.message.delete()
            embed = hikari.Embed(title='Profanity detected',
                                 description=f'{event.author.mention}, you have been muted for 5 minutes.',
                                 color=0xFF0000)
            embed.timestamp = event.message.created_at
            await channel.send(embed=embed)

            await event.member.edit(communication_disabled_until=datetime.now(timezone.utc) + timedelta(minutes=5))

            # Logging
            embed = hikari.Embed(title=f'Mute',
                                 description=f'{event.author.mention} received a timeout of 5 minutes. \nReason: '
                                             f'Profanity detected.',
                                 color=0xFF0000)
            embed.timestamp = event.message.created_at
            embed.add_field(name='Message--', value=f"**in <#{event.channel_id}>**\n> {event.message.content}")
            await bot.cache.get_guild_channel(
                json.load(open('config.json', 'r'))['logging_channel'][str(event.guild_id)]).send(embed=embed)
            log_file = json.load(open('warn_count.json', 'r'))
            log_file[str(event.author.id)] = log_file.get(str(event.author.id), 0) + 1
            json.dump(log_file, open('warn_count.json', 'w'), indent=4)
            if log_file[str(event.author.id)] >= 5:
                config = json.load(open('config.json', 'r'))
                await event.member.edit(roles=[config["muted_role"][str(event.guild_id)]])
                embed = hikari.Embed(title='Profanity Offense',
                                     description=f'{event.author.mention} has been given <@&{config["muted_role"][str(event.guild_id)]}> for '
                                                 f'their 6th profanity '
                                                 f'offense.',
                                     color=0xFF0000)
                embed.set_author(name=f"{event.message.author.username}#{event.message.author.discriminator}")
                embed.timestamp = event.message.created_at
            return


@bot.command
@lightbulb.command('filter', 'Add/remove a word from the filter list.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def msg_filter(ctx):
    pass


@msg_filter.child
@lightbulb.option('words', 'Word(s) to add to the profanity list.', type=str, required=True)
@lightbulb.command('add', 'Add a word to the filter list.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add_filter(ctx):
    with open('en.txt', 'r') as f:
        profanity = f.read().splitlines()
    with open('en.txt', 'a') as f:
        try:
            w = ctx.options.words.lower().split(' ')
            for i in w:
                if w[i] in profanity:
                    await ctx.reply(f'||{w[i]}|| is already in the filter list.')
                    return
        except TypeError:
            f.write(f'{i}\n')
            await ctx.respond(f'||{w}|| has been added to the filter list.')


@msg_filter.child
@lightbulb.command('remove', 'Remove a word from the filter list.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def remove_filter(ctx):
    with open('en.txt', 'r') as f:
        profanity = f.read().splitlines()
    with open('en.txt', 'w') as f:
        try:
            w = ctx.options.words.lower().split(' ')
            for i in w:
                if w[i] not in profanity:
                    await ctx.reply(f'||{w[i]}|| is not in the filter list.')
                    return
        except TypeError:
            for i in profanity:
                if i not in w:
                    f.write(f'{i}\n')
            await ctx.respond(f'||{w}|| has been removed from the filter list.')


bot.run()
