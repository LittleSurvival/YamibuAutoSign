import aiohttp
import time
import re
from typing import Any, Dict

class YamiboLogin:
    def __init__(self, username: str, password: str, safety_question: str, safety_answer: str):
        """
        :param username: Your Yamibo username.
        :param password: Your Yamibo password.
        :param safety_question: One of {'0','1','2','3','4','5','6','7'}.
                                '0' means "no security question" or "ignore it".
        :param safety_answer: The answer for the security question (used only if safety_question != '0').
        """
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
            "name": self.username,
            "cookies": {},
            "timestamp": int(time.time()),
            "good": False
        }
        login_url = "https://bbs.yamibo.com/member.php?mod=logging&action=login"

        async with aiohttp.ClientSession() as session:
            async with session.get(login_url) as resp:
                login_page_html = await resp.text()
            
            form_data = {
                "username": self.username,
                "password": self.password,
                "questionid": self.safety_question,
            }
            if self.safety_question != "0":
                form_data["answer"] = self.safety_answer

            post_url = (
                "https://bbs.yamibo.com/"
                "member.php?mod=logging&action=login&loginsubmit=yes&inajax=1"
            )

            async with session.post(post_url, data=form_data) as resp:
                text_response = await resp.text()

            cookies_from_jar = {}
            for cookie in session.cookie_jar:
                cookies_from_jar[cookie.key] = cookie.value

            account["cookies"] = cookies_from_jar

            has_auth_cookie = any("auth" in c.lower() for c in cookies_from_jar)
            if not has_auth_cookie:
                match_error = re.search(
                    r'<div id="messagetext".*?<p>([^<]+)</p>',
                    text_response,
                    re.DOTALL
                )
                if match_error:
                    reason = match_error.group(1).strip()
                    print(f"Login failed: {reason}")
                else:
                    print("Login failed: Could not find a specific error message.")
            else:
                account["good"] = True

        return account