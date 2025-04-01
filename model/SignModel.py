import re

class SignModel:
    LINK = 'https://bbs.yamibo.com/plugin.php?id=zqlj_sign'
    
    def __init__(self, name, cookies):
        self.name = name
        self.cookie = cookies
        self.status = False
        
    