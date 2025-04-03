import discord
from discord.ext import commands
import bot
from model.SignModel import SignModel
from model.DataModel import DataModel

class SignCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="sign", description="Perform daily sign-in")
    async def sign(self, interaction: discord.Interaction):
        loading_embed = discord.Embed(
            title="Sign In",
            description="Please wait while we sign in...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        
        account = await bot.db.read_account_by_id(interaction.user.id)
        if not account:
            embed = discord.Embed(
                title="Sign Failed",
                description="No account found. Please log in using the /login command first.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        sign_instance = SignModel(name=account["name"], cookies=account["cookies"])
       
        result = await sign_instance.sign()  # {"success": bool, "info": str}
        
        if result.get("success"):
            result_embed = discord.Embed(
                title="Sign Successful",
                description=result.get("info", "Sign-in succeeded."),
                color=discord.Color.green()
            )
        else:
            result_embed = discord.Embed(
                title="Sign Failed",
                description=result.get("info", "Sign-in failed."),
                color=discord.Color.red()
            )

        await interaction.edit_original_response(embed=result_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(SignCog(bot))