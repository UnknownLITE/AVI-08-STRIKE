import os

import discord
import requests
import schedule
from bs4 import BeautifulSoup
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or(">"), case_insensitive=True)


@bot.event
async def on_ready():
    schedule.every().monday.at("00:00").do(Stats_Update)
    print(f"Logged on as {bot.user}|{bot.user.id}")


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


async def Stats_Update():
    print("Stats Update Started...")
    channel = bot.get_channel(916717503982493816)
    async with channel.typing():
        embed = discord.Embed(title=f"AOS Stats",
                              description=create_embed("AOS"),
                              color=0x00ff00)
    await channel.send(embed=embed)

    channel = bot.get_channel(916717604159238214)
    async with channel.typing():
        embed = discord.Embed(title=f"STRIKE Stats",
                              description=create_embed("STRIKE"),
                              color=0x00ff00)
    await channel.send(embed=embed)


bot.run(os.environ["TOKEN"])
