import discord
from model.LoginModel import YamiboLogin
from model.DataModel import DataModel
from discord.ext import commands

class LoginModal(discord.ui.Modal, title="Yamibo Login"):
    username = discord.ui.TextInput(
        label="Username",
        placeholder="Enter your Yamibo username",
        required=True
    )
    password = discord.ui.TextInput(
        label="Password",
        placeholder="Enter your password",
        required=True,
        style=discord.TextStyle.short
    )
    safety_question = discord.ui.TextInput(
        label="Safety Question ID (0-7)",
        placeholder="0 means no security question",
        required=True
    )
    safety_answer = discord.ui.TextInput(
        label="Safety Answer",
        placeholder="Enter safety answer (if applicable)",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        loading_embed = discord.Embed(
            title="Logging In",
            description="Please wait while we log you in...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        
        login_instance = YamiboLogin(
            username=self.username.value,
            password=self.password.value,
            safety_question=self.safety_question.value,
            safety_answer=self.safety_answer.value
        )
        account = await login_instance.login()
        
        db = DataModel()
        db.save_account(account)

        if account.get("good"):
            result_embed = discord.Embed(
                title="Login Successful",
                description=f"Welcome {account['name']}!\nTimestamp: {account['timestamp']}",
                color=discord.Color.green()
            )
            cookies_str = "\n".join(f"{k}: {v}" for k, v in account["cookies"].items()) or "No cookies found."
            result_embed.add_field(name="Cookies", value=cookies_str, inline=False)
        else:
            error_msg = account.get("error", "Login failed.")
            result_embed = discord.Embed(
                title="Login Failed",
                description=error_msg,
                color=discord.Color.red()
            )
        await interaction.followup.send(embed=result_embed, ephemeral=True)

class LoginCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="login", description="Login to Yamibo")
    async def login(self, interaction: discord.Interaction):
        """Trigger the Yamibo login modal."""
        modal = LoginModal()
        await interaction.response.send_modal(modal)

def setup(bot: commands.Bot):
    bot.add_cog(LoginCog(bot))