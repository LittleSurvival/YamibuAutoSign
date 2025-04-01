import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    for filename in os.listdir("./command"):
        if filename.endswith(".py"):
            bot.load_extension(f"command.{filename[:-3]}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()

async def main():
    async with bot:
        await load_extensions()
        with open("setup/config.yaml", "r") as file:
            import yaml
            config = yaml.safe_load(file)
            await bot.start(config['bot_token'])

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())