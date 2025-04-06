import aiohttp
import re
from typing import Dict
import var

class SignModel:
    def __init__(self, name: str, cookies: dict):
        self.name = name
        self.cookie = cookies
        self.status = False

    async def sign(self) -> Dict[str, object]:
        """
        Performs the sign operation.
        
        1. Fetch the sign page at LINK.
        2. Extract the <a> tag with class "btna" (which contains the href for signing).
        3. Visit that URL.
        4. Extract the message text from the <div id="messagetext"> block.
        
        Returns:
            A dictionary with:
              - "success": bool, whether the sign operation was successful.
              - "info": str, the message extracted (or an error message if something failed).
        """
        try:
            async with aiohttp.ClientSession(cookies=self.cookie) as session:
                async with session.get(var.SIGN_URL, timeout=15) as resp:
                    text = await resp.text()

                match = re.search(r'<a\s+href="([^"]+)"\s+class="btna">', text)
                if not match:
                    print(text)
                    return {"success": False, "info": "Sign button not found. Possibly already signed or page structure changed."}

                sign_href = match.group(1)
                if not sign_href.startswith("http"):
                    sign_href = sign_href.lstrip("./")
                    sign_url = var.DOMAIN + sign_href
                else:
                    sign_url = sign_href

                async with session.get(sign_url) as sign_resp:
                    sign_text = await sign_resp.text()

                # This regex captures the text inside the first <p> within the <div id="messagetext" ...>
                message_match = re.search(r'<div\s+id="messagetext"[^>]*>.*?<p>(.*?)</p>', sign_text, re.DOTALL)
                if message_match:
                    message = message_match.group(1).strip()
                    try:
                        message = message.split("<script")[0]
                    except: pass
                    self.status = True
                    return {"success": True, "info": message}
                else:
                    return {"success": False, "info": "Failed to extract sign result message. The page may not have the expected content."}
        except Exception as e:
            return {"success": False, "info": f"Error during sign operation: {str(e)}"}
    
    