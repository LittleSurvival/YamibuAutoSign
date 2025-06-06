import asyncio
from datetime import datetime, timedelta
import discord
import bot
from model.SignModel import SignModel
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
         1. Calculate the initial next_run time.
         2. Wait until next_run using an adaptive smart delay loop.
         3. When the time is reached, run the sign process.
         4. After processing, calculate the next_run for the following day and loop.
        """
        now = datetime.now()
        target_time_obj = datetime.strptime(self.scheduled_time, "%H:%M:%S").time()

        # Initial calculation for current_next_run
        current_next_run = datetime.combine(now.date(), target_time_obj)
        if current_next_run < now:
            current_next_run += timedelta(days=1)
        
        print(f"[Service] Initializing. First run scheduled at: {current_next_run}")

        while True:
            now = datetime.now() 
            delay = (current_next_run - now).total_seconds()

            if delay > 0:
                print(f"[Service] Current time: {now}. Next run at: {current_next_run}. Waiting for {delay:.0f} seconds.")
                while delay > 0:
                    sleep_interval = min(60, delay) 
                    await asyncio.sleep(sleep_interval)
                    now = datetime.now() 
                    delay = (current_next_run - now).total_seconds() 
                    if delay > 0: 
                        print(f"[Service] Checking... {delay:.2f} seconds remaining until {current_next_run}.")
            
            print(f"[Service] Scheduled time {current_next_run} reached (current time: {datetime.now()}). Running sign process.")
            await self.run_sign_process()
            process_completion_time = datetime.now()
            print(f"[Service] Sign process completed at {process_completion_time}.")

            current_next_run = datetime.combine(current_next_run.date() + timedelta(days=1), target_time_obj)
            print(f"[Service] Next run scheduled for: {current_next_run}.")
            
            await asyncio.sleep(1)

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
        
        accounts = await bot.db.get_autosign_accounts()
        
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

        max_retries = 3
        retry_delay = 5

        for idx, account in enumerate(accounts, start=1):
            sign_instance = SignModel(account.username, account.cookies)
            
            result = {"success": False, "info": "Initial attempt failed"}
            for attempt in range(max_retries):
                result = await sign_instance.sign()
                if result.get("success"):
                    break
                elif attempt < max_retries - 1:
                    print(f"[Service] Sign failed for {account.username}, retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)

            if result.get("success"):
                success_count += 1
                details.append(f"{account.username}: Success - {result.get('info', 'Sign-in succeeded.')}")
            else:
                failed_count += 1
                details.append(f"{account.username}: Failed after {max_retries} attempts - {result.get('info', 'Sign-in failed.')}")
                
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