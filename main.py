import asyncio
import os
from datetime import time

import aiomysql
import nextcord
import requests
from bs4 import BeautifulSoup
from nextcord.ext import commands, tasks

bot = commands.Bot(command_prefix=commands.when_mentioned_or("."), case_insensitive=True,
                   intents=nextcord.Intents.all())

bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}|{bot.user.id}")
    # Stats_Update.start()
    update_nick.start()
    
def nick_scrap(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")
    raw = soup.find("div", class_="page-header")
    if len(raw.text) > 2:
        nick = raw.text.replace("  ", "").split("\n")[1]
        return nick
    else:
        return "Invalid"


@bot.command(aliases=["nick"])
async def link(ctx, stats_link, member: nextcord.Member = None):
    if member is None or member.id == ctx.author.id:
        member = ctx.author
    if member is not None and not ctx.author.guild_permissions.administrator and not ctx.author.id == member.id or member.bot:
        await ctx.message.add_reaction("🚫")
        return
    if stats_link.startswith("https://stats.warbrokers.io/players/i/"):
        url = stats_link
    else:
        url = f"https://stats.warbrokers.io/players/i/{stats_link}"
    with ctx.channel.typing():
        # r = requests.get(url)
        if nick_scrap(url) == "Invalid":
            msg = await ctx.send(content=f"Invalid :x:")
            await ctx.message.add_reaction("❌")
            await asyncio.sleep(1)
            await msg.delete()
            return
        else:
            await member.edit(nick=nick_scrap(url))
            await ctx.message.add_reaction("✅")

    conn = await aiomysql.connect(host='remotemysql.com', port=3306,
                                  user='PhVgPxDJdd', password='OWKglFnGUr', db='PhVgPxDJdd')

    cur = await conn.cursor()
    await cur.execute("SELECT * FROM WB_Nickname;")
    for i in await cur.fetchall():
        if i[0] == member.id:
            await cur.execute(f"UPDATE WB_Nickname SET player_id = '{url[-24:]}' WHERE user_id = {member.id};")
            await conn.commit()
            await cur.close()
            return
    await cur.execute(
        f"INSERT INTO `WB_Nickname` (`user_id`, `player_id`) VALUES ('{member.id}', '{url[-24:]}');")
    await conn.commit()
    await cur.close()
    return


@link.error
async def chnick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument :warning:\nRun `{ctx.prefix}nick [link_to_stats/player_id]`")
    else:
        raise error

@bot.command()
async def unlink(ctx, * , member: nextcord.Member = None):
    if member is None or member.id == ctx.author.id:
        member = ctx.author
    if member is not None and not ctx.author.guild_permissions.administrator and not ctx.author.id == member.id or member.bot:
        await ctx.message.add_reaction("🚫")
        return
    conn = await aiomysql.connect(host='remotemysql.com', port=3306,
                                  user='PhVgPxDJdd', password='OWKglFnGUr', db='PhVgPxDJdd')

    cur = await conn.cursor()
    await cur.execute("SELECT * FROM WB_Nickname;")
    for i in await cur.fetchall():
        if i[0] == member.id:
            await cur.execute(f"DELETE FROM WB_Nickname WHERE user_id = {member.id};")
            await conn.commit()
            await cur.close()
            return
    await cur.close()
    await member.edit(nick=None)
    await ctx.message.add_reaction("<:kill:927889321023918110>")
    return

@tasks.loop(time=[time(hour=00, minute=00)])
async def update_nick():
    conn = await aiomysql.connect(host='remotemysql.com', port=3306,
                                  user='PhVgPxDJdd', password='OWKglFnGUr', db='PhVgPxDJdd')

    cur = await conn.cursor()
    await cur.execute("SELECT * FROM WB_Nickname;")
    for i in await cur.fetchall():
        await bot.get_guild(867986226458808360).get_member(int(i[0])).edit(nick=nick_scrap('https://stats.warbrokers.io/players/i/' + i[1]))


bot.run(os.environ['TOKEN'])
