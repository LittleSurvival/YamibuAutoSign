import discord
import os
import var
import asyncio

from discord.ext import commands
from model.DataModel import DataModel
from service import service_autosign

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
db = DataModel()

async def load_extensions():
    for root, dirs, files in os.walk("./command"):
        for filename in files:
            if filename.endswith(".py") and not '__init__' in filename:
                module_path = os.path.join(root, filename)[2:-3].replace(os.path.sep, ".")
                await bot.load_extension(module_path)
                print(f"Extension loaded: {module_path}")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")
    
    """
    Auto Sign Service
    """
    autosign = service_autosign.DailySignService(bot=bot)
    asyncio.create_task(autosign.start_service())
    
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.reply(f"Hello {message.author.mention}!")
    await bot.process_commands(message)

async def launch():
    await db.create_table()
    async with bot:
        await load_extensions()
        await bot.start(var.BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(launch())