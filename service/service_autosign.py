import asyncio
import yaml
from datetime import datetime, timedelta
import discord
import bot
from model.SignModel import SignModel
from model.DataModel import DataBase
import var

class DailySignService:
    def __init__(self, bot: discord.Client):
        self.scheduled_time = var.AUTOSIGN_SCHEDULED_TIME
        self.channel_id = var.AUTOSIGN_NOTIFY_CHANNEL_ID
        self.check_delay = var.AUTOSIGN_CHECK_DELAY
        self.bot = bot

    async def start_service(self):
        """
        Main loop:
         1. Wait until the scheduled time using an adaptive smart delay loop.
         2. When the time is reached, run the sign process.
         3. After processing, loop back to wait for the next day.
        """
        while True:
            now = datetime.now()
            # Parse scheduled time (hh:mm:ss)
            target_time = datetime.strptime(self.scheduled_time, "%H:%M:%S").time()
            next_run = datetime.combine(now.date(), target_time)
            if next_run < now:
                next_run += timedelta(days=1)
            delay = (next_run - now).total_seconds()
            print(f"[Service] Current time: {now}. Next run at: {next_run}. Total delay: {delay:.0f} seconds.")

           
            while delay > 0:
                if delay > 300:
                    chosen_interval = delay - 300
                elif delay > 60:
                    chosen_interval = 60
                elif delay > 5:
                    chosen_interval = 5
                else:
                    chosen_interval = 1
                sleep_interval = min(chosen_interval, delay)
                await asyncio.sleep(sleep_interval)
                now = datetime.now()
                delay = (next_run - now).total_seconds()
                print(f"[Service] Checking... Remaining delay: {delay:.2f} seconds.")

            await self.run_sign_process()

    async def run_sign_process(self):
        """
        Processes all accounts by performing the sign action for each.
        Updates a progress embed in a specified Discord channel.
        """
        print(f"[Service] Sign process started at {datetime.now()}")
        
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print("[Service] Error: Log channel not found.")
            return
        
        loading_embed = discord.Embed(
            title="Daily Sign Process",
            description="Loading accounts from database...",
            color=discord.Color.gold()
        )
        loading_embed.set_footer(text="Please wait...")
        loading_message = await channel.send(embed=loading_embed)
        
        accounts = await bot.db.get_all_accounts()
        
        total = len(accounts)
        success_count = 0
        failed_count = 0
        details = []
        
        progress_embed = discord.Embed(
            title="Daily Sign Progress",
            description="Starting sign process...",
            color=discord.Color.blue()
        )
        progress_embed.add_field(name="Total Accounts", value=str(total), inline=True)
        progress_embed.add_field(name="Success", value="0", inline=True)
        progress_embed.add_field(name="Failed", value="0", inline=True)
        progress_embed.set_footer(text="Progress: 0%")
        await loading_message.edit(embed=progress_embed)

        for idx, account in enumerate(accounts, start=1):
            sign_instance = SignModel(account["name"], account["cookies"])
            result = await sign_instance.sign()
            if result.get("success"):
                success_count += 1
                details.append(f"{account['name']}: Success - {result.get('info')}")
            else:
                failed_count += 1
                details.append(f"{account['name']}: Failed - {result.get('info')}")
                
            await asyncio.sleep(self.check_delay)

            if idx % 100 == 0 or idx == total:
                progress_percentage = (idx / total) * 100
                bar_length = 20
                filled_length = int(round(bar_length * idx / total))
                progress_bar = "█" * filled_length + "-" * (bar_length - filled_length)
                progress_embed.description = f"Progress: [{progress_bar}] {progress_percentage:.1f}%"
                progress_embed.set_field_at(1, name="Success", value=str(success_count), inline=True)
                progress_embed.set_field_at(2, name="Failed", value=str(failed_count), inline=True)
                progress_embed.set_footer(text=f"Processed {idx}/{total} accounts")
                await loading_message.edit(embed=progress_embed)
                
        progress_embed.title = "Daily Sign Completed"
        progress_embed.description += "\nProcess finished."
        progress_embed.set_footer(text=f"Total: {total} | Success: {success_count} | Failed: {failed_count}")
        await loading_message.edit(embed=progress_embed)

        final_details = "\n".join(details[-20:])
        detail_embed = discord.Embed(
            title="Last 20 Sign Details",
            description=final_details if final_details else "No details available.",
            color=discord.Color.green()
        )
        await channel.send(embed=detail_embed)
        print(f"[Service] Sign process completed at {datetime.now()}")