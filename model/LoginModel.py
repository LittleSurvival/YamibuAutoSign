import asyncio
from random import seed
from tkinter import Variable
import aiohttp
import time
import re
from typing import Any, Dict

import bot
import var

class YamiboLogin:
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

    async def login(self) -> Dict[str, Any]:
        """
        Attempt to log in to Yamibo. Returns a dict with:
            - name:       self.username
            - cookies:    { cookieName: cookieValue, ... }
            - timestamp:  current epoch time
            - good:       Boolean indicating if the login is likely successful
        Prints an error reason if login fails (i.e., if no cookie name contains "auth").
        """
        account = {
            "discordUserId": self.discordUserId,
            "discordGuildId": self.discordGuildId,
            "name": self.username,
            "cookies": {},
            "timestamp": int(time.time()),
            "good": False
        }

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
                
                account["cookies"] = cookies_from_jar
                
                if len(cookies_from_jar) != 2:
                    if self.safety_answer:
                        text_response = text_response.replace(self.safety_answer, '*' * len(self.safety_answer))
                    text_response = text_response.replace(self.password, '*' * len(self.password))
                    account["error"] = f"Login failed: {text_response}"
                    
                    return account
                else:
                    account["good"] = True
                    account["message"] = self.parse_success_xml_to_text(text_response)
                    
                    await bot.db.save_account(account)
                    
                    return account
                    
        except asyncio.TimeoutError:
            account["error"] = "Login failed: Timeout."

        return account
    
    def parse_success_xml_to_text(self, text_response: str) -> str:
        """
        This regex does the following:
        1. Finds the portion setting $('succeedlocation').innerHTML = '...';
        2. Captures three parts:
            - Group1: Text before the <font> tag (e.g. "欢迎您回来，")
            - Group2: The text inside the <font> tag (e.g. "百合花蕾")
            - Group3: The text immediately following the </font> up until a delimiter (here we assume it ends before a "，" or the closing quote)
        """
        pattern = r"\$\('succeedlocation'\)\.innerHTML\s*=\s*'([^<]+)<font[^>]+>([^<]+)</font>\s*([^，']+)"
        match = re.search(pattern, text_response)

        if match:
            part1 = match.group(1)  # Expected: "欢迎您回来，"
            part2 = match.group(2)  # Expected: "百合花蕾"
            part3 = match.group(3)  # Expected: "thenano"
            result = part1.strip() + " " + part2.strip() + " " + part3.strip()
            return result  # Output: 欢迎您回来， 百合花蕾 thenano
        else:
            return text_response