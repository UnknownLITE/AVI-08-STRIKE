import os
import random
from datetime import datetime, time

import nextcord
import requests
from bs4 import BeautifulSoup
from nextcord.ext import commands, tasks
from nextcord.utils import utcnow

bot = commands.Bot(command_prefix=commands.when_mentioned_or("~"), case_insensitive=True)


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}|{bot.user.id}")
    Stats_Update.start()


def stats_scrape(squad):
    url = f"https://stats.warbrokers.io/squads/{squad}"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    raw = (soup.find("div", class_="squad-top-ten-weapons-grid")).text

    raw = raw.replace("\n\n", "")
    w = raw.split("\n")
    q = {w[0]: w[1], w[2]: w[3], w[4]: w[5], w[6]: w[7], w[8]: w[9], w[10]: w[11], w[12]: w[13]}
    return q


def create_embed(squad):
    q = stats_scrape(squad)
    data = f"""```py
Deathmatch wins:        {q["Death Match"]}
Missile Launch:         {q["Missile Launch"]}
Battle Royale wins:     {q["Battle Royale"]}
Package Drop:           {q["Package Drop"]}
Vehicle escort:         {q["Vehicle Escort"]}
Capture point:          {q["Capture Point"]}
Zombie BR wins:         {q["Zombie BR"]}```"""
    return data


@tasks.loop(time=[time(hour=00, minute=00)])
async def Stats_Update():
    if utcnow().strftime("%A") != "Monday":
        return
    print(f"Stats Update Started... for {datetime.now()}")
    channel = bot.get_channel(916717503982493816)
    async with channel.typing():
        embed = nextcord.Embed(title=f"AOS Stats",
                               description=create_embed("AOS"),
                               color=0x00ff00)
    await channel.send(embed=embed)

    channel = bot.get_channel(916717604159238214)
    async with channel.typing():
        embed = nextcord.Embed(title=f"STRIKE Stats",
                               description=create_embed("STRIKE"),
                               color=0x00ff00)
    await channel.send(embed=embed)
    print(f"Stats Update Finished... for {datetime.now()}")


@bot.command(aliases=["m", "member"])
async def members(ctx, *, squad):
    url = f"https://stats.warbrokers.io/squads/{squad}"
    async with ctx.channel.typing():
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        raw = soup.find_all("div", class_="squad-player-header")
        e = nextcord.Embed(title=f"*`Members`*", colour=0x00ff00)
        for i in range(len(raw)):
            q = raw[i].text.replace("\n", "")
            q = q.replace("\n", "")
            e.set_author(name=f"[{squad}]", url=url, icon_url="https://warbrokers.io/img/ui_logo_200.png")
            e.add_field(name="\u200B", value=f"{i + 1}. __[`{q}`](https://stats.warbrokers.io{raw[i].a['href']})__")
            e.set_image(url=f"https://stats.warbrokers.io/images/backgrounds/banner-{random.randint(1, 20)}.jpg")
    await ctx.send(embed=e)

bot.run(os.environ["TOKEN"])
