import discord
from discord.ext import commands

class HelpEmbed:
    @staticmethod
    def get_embed() -> discord.Embed:
        embed = discord.Embed(
            title="指令列表",
            description="Yamichan说明书",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="/login",
            value="使用 Cookie 或账号密码登录百合会，启用自动签到等功能。",
            inline=False
        )
        embed.add_field(
            name="/sign",
            value="使用指令打卡，登录后使用该指令即可启用。",
            inline=False
        )
        embed.add_field(
            name="/autosign",
            value="启用自动打卡，登录后使用该指令即可启用。",
            inline=False
        )
        
        embed.set_footer(text="Dev thenano")
        return embed

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="help", description="打开说明书")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=HelpEmbed.get_embed(), ephemeral=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))