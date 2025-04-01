import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    for filename in os.listdir("./command"):
        if filename.endswith(".py") and not '__init__' in filename:
            await bot.load_extension(f"command.{filename[:-3]}")
            print(f"Extension loaded: {filename}")

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=1356206853855383652))
    print(f"Logged in as {bot.user}")
    
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.reply(f"Hello {message.author.mention}!")
    await bot.process_commands(message)


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