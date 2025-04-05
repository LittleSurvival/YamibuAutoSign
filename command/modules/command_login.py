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

import discord

class CookieLoginEmbed:
    @staticmethod
    def get_embed() -> discord.Embed:
        embed = discord.Embed(
            title="如何使用 Cookie 登入百合会",
            description=(
                "以下步骤将指导您如何获取并填写 Cookie。\n"
                "请注意：此方法仅适用于电脑端浏览器。"
            ),
            color=discord.Color.blue()
        )
        embed.set_image(url="https://github.com/LittleSurvival/YamibuAutoSign/blob/main/docs/cookie_location.png?raw=true")
        
        steps = (
            "**1. 打开 [百合会](https://bbs.yamibo.com/) 并完成登录。**\n"
            "   - 确保您已经成功登录到自己的账号。\n\n"
            "**2. 打开开发者工具：**\n"
            "   - 按下 **F12** 或同时按下 **Ctrl + Shift + I**。\n\n"
            "**3. 进入 Application 面板：**\n"
            "   - 在打开的开发者工具中，找到并点击 **Application**（或中文“应用”）\n"
            "   - 左侧找到 **Cookies** 并点击。\n\n"
            "**4. 查找 Cookie：**\n"
            "   - 在 Cookies 列表中，找到 **EeqY_2132_auth** 和 **EeqY_2132_saltkey**。\n\n"
            "**5. 复制并填写：**\n"
            "   - 将 `EeqY_2132_auth` 的值复制后，填入我们程序中的 **auth** 字段。\n"
            "   - 将 `EeqY_2132_saltkey` 的值复制后，填入 **saltkey** 字段。\n\n"
            "完成以上步骤后，程序即可使用您的 Cookie 信息进行自动登录。"
        )
        embed.add_field(name="步骤说明", value=steps, inline=False)
        embed.set_footer(text="确保按顺序操作即可。祝使用愉快！")
        return embed

class LoginCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="login", description="Login to Yamibo")
    @discord.app_commands.describe(mode="Select login mode: Password or Cookie")
    @discord.app_commands.choices(mode=[
        discord.app_commands.Choice(name="Password", value="password"),
        discord.app_commands.Choice(name="Cookie", value="cookie"),
        discord.app_commands.Choice(name="How to Login with cookie?", value="help"),
    ])
    async def login(self, interaction: discord.Interaction, mode: str):
        if mode == "help":
            await interaction.response.send_message(embed=CookieLoginEmbed.get_embed(), ephemeral=True)
            return
        elif mode == "password":
            modal = CommandLoginbyPasswordModal()
        elif mode == "cookie":
            modal = CommandLoginbyCookieModal()
        else:
            await interaction.response.send_message("Invalid login mode.", ephemeral=True)
            return
        await interaction.response.send_modal(modal)

async def setup(bot: commands.Bot):
    await bot.add_cog(LoginCog(bot))