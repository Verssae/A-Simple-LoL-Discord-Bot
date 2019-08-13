import discord
import json

from discord.ext import commands

# get data
with open("config.json", "r") as f:
    data = json.load(f)
    version = data.get("version").strip()
    apikey = data.get("apikey")
    token = data.get("token")
    prefix = data.get("prefix")

bot = commands.Bot(command_prefix=prefix)
cogs = ['cogs.lol']

if __name__ == '__main__':
    for cog in cogs:
        try:
            bot.load_extension(cog)
        except Exception as error:
            print(f'cog {cog} cannot be loaded. [{error}]')

    bot.run(token)