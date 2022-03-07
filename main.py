import asyncio
from datetime import datetime

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
    if member is not None and not ctx.author.guild_permissions.administrator and not ctx.author.id == member.id or member.bot:
        await ctx.message.add_reaction("🚫")
        return
    if member is None:
        member = ctx.author
    if stats_link.startswith("https://stats.warbrokers.io/players/i/"):
        url = stats_link
    else:
        url = f"https://stats.warbrokers.io/players/i/{stats_link}"
    async with ctx.channel.typing():
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
        embed = nextcord.Embed(title="Something went wrong!! :warning:", description=f"> `{error}`",
                               color=nextcord.Color.red())
        await ctx.send(f"Calling <@794913278371168257> for help!", embed=embed)
        await ctx.message.add_reaction("⚠")


@bot.command()
async def unlink(ctx, *, member: nextcord.Member = None):
    if member is None:
        member = ctx.author
    if member is not None and not ctx.author.guild_permissions.administrator and not ctx.author.id == member.id or member.bot:
        await ctx.message.add_reaction("🚫")
        return
    conn = await aiomysql.connect(host='remotemysql.com', port=3306,
                                  user='PhVgPxDJdd', password='OWKglFnGUr', db='PhVgPxDJdd')

    cur = await conn.cursor()
    if await cur.execute(f"SELECT * FROM WB_Nickname WHERE user_id = {member.id};") == 0:
        msg = await ctx.send(f"{member.mention}, you haven't linked to your stats.")
        await ctx.message.add_reaction("🚮")
        await asyncio.sleep(1)
        await msg.delete()
        await cur.close()
        return
    await cur.execute(f"DELETE FROM WB_Nickname WHERE user_id = {member.id};")
    await conn.commit()
    await member.edit(nick=None)
    await ctx.message.add_reaction("<:kill:927889321023918110>")
    await cur.close()
    return


@unlink.error
async def unlink_error(ctx, error):
    embed = nextcord.Embed(title="Something went wrong!! :warning:", description=f"> `{error}`",
                           color=nextcord.Color.red())
    await ctx.send(f"Calling <@794913278371168257> for help!", embed=embed)
    await ctx.message.add_reaction("⚠")


@tasks.loop(hours=1)
async def update_nick():
    t = datetime.now()
    print(f"🛠 Updating nicknames for {t}")
    conn = await aiomysql.connect(host='remotemysql.com', port=3306,
                                  user='PhVgPxDJdd', password='OWKglFnGUr', db='PhVgPxDJdd')

    cur = await conn.cursor()
    await cur.execute("SELECT * FROM WB_Nickname;")
    for i in await cur.fetchall():
        try:
            await bot.get_guild(867986226458808360).get_member(i[0]).edit(
                nick=nick_scrap(f'https://stats.warbrokers.io/players/i/{i[1]}'))
        except AttributeError:
            print(f"{i[0]} is not a member of ꜱᴛяɪᴋᴇ/ᴀᴏꜱ ᴏꜰꜰɪᴄɪᴀʟ|867986226458808360.\nRemoving from database.")
            await cur.execute(f"DELETE FROM WB_Nickname WHERE user_id = {i[0]};")
            await conn.commit()
            await cur.close()
            pass
    await cur.close()
    print(f"✅ Nicknames updated for {t}")
    return


bot.run(os.environ['TOKEN'])
