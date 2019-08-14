import discord
import json
from updated import check_version

from discord.ext import commands

# get data
with open("config.json", "r") as f:
    config = json.load(f)
    version = config.get("version").strip()
    apikey = config.get("apikey")
    token = config.get("token")
    prefix = config.get("prefix")

bot = commands.Bot(command_prefix=prefix)
cogs = ['cogs.lol']

if __name__ == '__main__':
    check_version(config)
    for cog in cogs:
        try:
            bot.load_extension(cog)
        except Exception as error:
            print(f'cog {cog} cannot be loaded. [{error}]')
    
    bot.run(token)