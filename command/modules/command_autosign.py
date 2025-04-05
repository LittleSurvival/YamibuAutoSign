from enum import auto
import discord
from discord.ext import commands
import bot

class AutoSignSwitchCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @discord.app_commands.command(name="autosign", description="Enable/Disable auto sign.")
    async def sign(self, interaction: discord.Interaction):
        account = await bot.db.read_account_by_id(interaction.user.id)
        if not account:
            embed = discord.Embed(
                title="自动签到",
                description="未找到账号。请先使用 /login 命令登录。",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            account.autosign = not account.autosign
            await bot.db.save_account(account)
            embed = discord.Embed(
                title="自动签到",
                description=f"已將自動簽到設定成 `{account.autosign}`",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
async def setup(bot: commands.Bot):
    await bot.add_cog(AutoSignSwitchCog(bot))