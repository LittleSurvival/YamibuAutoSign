import asyncio
import aiohttp
import time
import re

import bot
from model.DataModel import Account
import var

class YamiboLogin_Cookie:
    def __init__(self, discordUserId: int, discordGuildId: int, username: str, auth: str, saltkey: str):
        """
        :param discordUserId: The discord account your Yamibo account bind to.
        :param discordGuildId: The discord guild your Yamibo account auto login notification bind to.
        :param username: Your yamibo username(null as default, update after login successful).
        :param auth: cookie -> EeqY_2132_auth
        :param saltkey: cookie -> EeqY_2132_saltkey
        """
        self.discordUserId = discordUserId
        self.discordGuildId = discordGuildId
        self.username = username
        self.auth = auth
        self.saltkey = saltkey
    
    async def login(self) -> tuple[str, Account]:
        account = Account(
            discord_user_id=self.discordUserId,
            discord_guild_id=self.discordGuildId,
            username=self.username,
            cookies={
                "EeqY_2132_auth": self.auth,
                "EeqY_2132_saltkey": self.saltkey
            },
            timestamp=int(time.time()),
            good=False
        )
        message = "Login failed: Unknown Reason"
        
        try:
            async with aiohttp.ClientSession(cookies=account.cookies) as session:
                async with session.get(var.LOGIN_URL, timeout=15) as resp:
                    check_page_html = await resp.text()
                #Page not login in
                if "placeholder=\"用户名/Email/UID\"" in check_page_html:
                    message = f"Login failed : Cookie is not correct or already expired."
                    
                    return message, account
                else:
                    account.good = True
                    message = parse_success_xml_to_text(check_page_html)
                    print(message)
                    
                    await bot.db.save_account(account)
                    return message, account
        except TimeoutError:
            message = "Login failed: Timeout."
        
        return message, account

class YamiboLogin_Password:
    def __init__(self, discordUserId: int, discordGuildId: int, username: str, password: str, safety_question: str, safety_answer: str):
        """
        :param discordUserId: The discord account your Yamibo account bind to.
        :param discordGuildId: The discord guild your Yamibo account auto login notification bind to.
        :param username: Your Yamibo username.
        :param password: Your Yamibo password.
        :param safety_question: One of {'0','1','2','3','4','5','6','7'}.
                                '0' means "no security question" or "ignore it".
        :param safety_answer: The answer for the security question (used only if safety_question != '0').
        """
        self.discordUserId = discordUserId
        self.discordGuildId = discordGuildId
        self.username = username
        self.password = password
        self.safety_question = safety_question
        self.safety_answer = safety_answer

    async def login(self) -> tuple[str, Account]:
        """
        Attempt to log in to Yamibo using username and password.
        Returns:
            tuple: (message, Account) where:
                - message: Success or error message
                - Account: An Account object containing:
                    - discord_user_id: The Discord user ID
                    - discord_guild_id: The Discord guild ID
                    - username: Yamibo username
                    - cookies: Dictionary of authentication cookies
                    - timestamp: Current epoch time
                    - good: Boolean indicating if login was successful
        """
        account = Account(
            discord_user_id=self.discordUserId,
            discord_guild_id=self.discordGuildId,
            username=self.username,
            cookies={},
            timestamp=int(time.time()),
            good=False
        )
        message = "Login failed: Unknown Reason"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(var.LOGIN_URL, timeout=15) as resp:
                    login_page_html = await resp.text()
                    
                form_data = {
                    "username": self.username,
                    "password": self.password,
                    "questionid": self.safety_question,
                }
                if self.safety_question != "0":
                    form_data["answer"] = self.safety_answer

                async with session.post(var.LOGIN_POST_URL, data=form_data, timeout=15) as resp:
                    text_response = await resp.text()

                cookies_from_jar = {}
                for cookie in session.cookie_jar:
                    """
                    Yamibo only need two cookies to login :
                    EeqY_2132_auth : len(111) A-Za-z%
                    EeqY_2132_saltkey : len(25) A-Za-z
                    """
                    if "auth" in cookie.key or "saltkey" in cookie.key:
                        cookies_from_jar[cookie.key] = cookie.value
                
                account.cookies = cookies_from_jar
                
                if len(cookies_from_jar) != 2:
                    if self.safety_answer:
                        text_response = text_response.replace(self.safety_answer, '*' * len(self.safety_answer))
                    text_response = text_response.replace(self.password, '*' * len(self.password))
                    
                    message = f"Login failed: {text_response}"
                    return message, account
                else:
                    account.good = True
                    message = parse_success_xml_to_text(text_response)
                    
                    await bot.db.save_account(account)
                    return message, account
                    
        except asyncio.TimeoutError:
            message = "Login failed: Timeout."

        return message, account
    
def parse_success_xml_to_text(text_response: str) -> str:
        """
        Parse the login success message from the response text.
        This function handles two possible formats:
        1. JavaScript format: $('succeedlocation').innerHTML = '...';
        2. HTML format: <div id="messagetext" class="alert_right"><p>欢迎您回来，...</p>
        
        Returns a formatted success message.
        """
        js_pattern = r"\$\('succeedlocation'\)\.innerHTML\s*=\s*'([^<]+)<font[^>]+>([^<]+)</font>\s*([^，']+)"
        js_match = re.search(js_pattern, text_response)
        
        if js_match:
            part1 = js_match.group(1)  # Expected: "欢迎您回来，"
            part2 = js_match.group(2)  # Expected: "百合花蕾"
            part3 = js_match.group(3)  # Expected: "thenano"
            result = part1.strip() + " " + part2.strip() + " " + part3.strip()
            return result  # Output: 欢迎您回来， 百合花蕾 thenano
        
        html_pattern = r'<div id="messagetext" class="alert_right">\s*<p>([^<]+)<font[^>]+>([^<]+)</font>\s*([^<,]+)'
        html_match = re.search(html_pattern, text_response)
        
        if html_match:
            part1 = html_match.group(1)  # Expected: "欢迎您回来，"
            part2 = html_match.group(2)  # Expected: "百合花蕾"
            part3 = html_match.group(3).split("，")[0]  # Expected: "thenano"
            result = part1.strip() + " " + part2.strip() + " " + part3.strip()
            return result  # Output: 欢迎您回来， 百合花蕾 thenano
            
        return text_response