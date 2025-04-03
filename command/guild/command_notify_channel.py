import discord
from discord.ext import commands
import var

class NotifyChannelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @discord.app_commands.command(name="notifaction_channel", description="Set up the specific channel for sending notifaction.")
    async def set_channel(self, interaction: discord.Interaction):
        await interaction.response.send_message("not done")

async def setup(bot: commands.Bot):
    await bot.add_cog(NotifyChannelCog(bot))