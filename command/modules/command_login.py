import discord
from discord.ext import commands
from datetime import datetime
from model.LoginModel import YamiboLogin_Password, YamiboLogin_Cookie

class CommandLoginbyPasswordModal(discord.ui.Modal, title="Yamibo Login - Password Mode"):
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
        label="安全提问",
        placeholder="(未设置请輸入0)",
        default="0",
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
        
        login_instance = YamiboLogin_Password(
            discordUserId=interaction.user.id,
            discordGuildId=interaction.guild.id,
            username=self.username.value,
            password=self.password.value,
            safety_question=self.safety_question.value,
            safety_answer=self.safety_answer.value
        )
        message, account = await login_instance.login()
        timestamp_formatted = datetime.fromtimestamp(account.timestamp).strftime('%Y:%m:%d %H:%M:%S')
        
        if account.good:
            result_embed = discord.Embed(
                title="Login Successful",
                description=f"{message}!\nTimestamp: {timestamp_formatted}",
                color=discord.Color.green()
            )
        else:
            result_embed = discord.Embed(
                title="Login Failed",
                description=f"{message}\nTimestamp: {timestamp_formatted}",
                color=discord.Color.red()
            )
        await interaction.edit_original_response(embed=result_embed)

class CommandLoginbyCookieModal(discord.ui.Modal, title="Yamibo Login - Cookie Mode"):
    auth = discord.ui.TextInput(
        label="Auth",
        placeholder="Enter your auth cookie value",
        required=True
    )
    saltkey = discord.ui.TextInput(
        label="Saltkey",
        placeholder="Enter your saltkey cookie value",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        loading_embed = discord.Embed(
            title="Logging In",
            description="Please wait while we log you in...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        
        login_instance = YamiboLogin_Cookie(
            discordUserId=interaction.user.id,
            discordGuildId=interaction.guild.id,
            username="undefined",
            auth=self.auth.value,
            saltkey=self.saltkey.value
        )
        message, account = await login_instance.login()
        timestamp_formatted = datetime.fromtimestamp(account.timestamp).strftime('%Y:%m:%d %H:%M:%S')
        
        if account.good:
            result_embed = discord.Embed(
                title="Login Successful",
                description=f"{message}!\nTimestamp: {timestamp_formatted}",
                color=discord.Color.green()
            )
        else:
            result_embed = discord.Embed(
                title="Login Failed",
                description=f"{message}\nTimestamp: {timestamp_formatted}",
                color=discord.Color.red()
            )
        await interaction.edit_original_response(embed=result_embed)

class LoginCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="login", description="Login to Yamibo")
    @discord.app_commands.describe(mode="Select login mode: Password or Cookie")
    @discord.app_commands.choices(mode=[
        discord.app_commands.Choice(name="Password", value="password"),
        discord.app_commands.Choice(name="Cookie", value="cookie")
    ])
    async def login(self, interaction: discord.Interaction, mode: str):
        if mode == "password":
            modal = CommandLoginbyPasswordModal()
        elif mode == "cookie":
            modal = CommandLoginbyCookieModal()
        else:
            await interaction.response.send_message("Invalid login mode.", ephemeral=True)
            return
        await interaction.response.send_modal(modal)

async def setup(bot: commands.Bot):
    await bot.add_cog(LoginCog(bot))