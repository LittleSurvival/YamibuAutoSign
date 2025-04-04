import discord
from discord.ext import commands
import bot
import var

class NotifyChannelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @discord.app_commands.command(name="notifaction_channel", description="Set up the specific channel for sending notifaction.")
    async def set_channel(self, interaction: discord.Interaction):
        loading_embed = discord.Embed(
            title="Setting channel...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=loading_embed)
        
        await bot.db.save_notify_channels(interaction.guild.id,)

async def setup(bot: commands.Bot):
    await bot.add_cog(NotifyChannelCog(bot))