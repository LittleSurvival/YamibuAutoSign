import yaml
import os

"""
LOAD/DEFAULT CONFIG
"""

autosign_path = "setup/autosign.yaml"
config_path = "setup/config.yaml"

if not os.path.exists(autosign_path):
    os.makedirs(os.path.dirname(autosign_path), exist_ok=True)
    default_autosign = {
        "scheduled_time": "3:00:00",
        "check_delay": 5,
        "guild_id": None,
        "channel_id": None
    }
    with open(autosign_path, "w") as file:
        yaml.dump(default_autosign, file)

if not os.path.exists(config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    default_autosign = {
        "scheduled_time": "3:00:00",
        "check_delay": 5,
        "guild_id": None,
        "channel_id": None
    }
    with open(config_path, "w") as file:
        yaml.dump(default_autosign, file)

with open(autosign_path, "r") as file:
    autosign = yaml.safe_load(file)

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

"""
STATIC VALUES
"""

DOMAIN = "https://bbs.yamibo.com/"
GUILD_ID = "1356206853855383652"

LOGIN_URL = "https://bbs.yamibo.com/member.php?mod=logging&action=login"
LOGIN_POST_URL = "https://bbs.yamibo.com/member.php?mod=logging&action=login&loginsubmit=yes&inajax=1"
LOGIN_CHECK_URL = "https://bbs.yamibo.com/forum-49-1.html" #文學區首頁

SIGN_URL = "https://bbs.yamibo.com/plugin.php?id=zqlj_sign"

BOT_TOKEN = config['bot_token']
    
AUTOSIGN_SCHEDULED_TIME = autosign["scheduled_time"]
AUTOSIGN_CHECK_DELAY = autosign["check_delay"]
AUTOSIGN_NOTIFY_GUILD_ID = autosign["guild_id"]
AUTOSIGN_NOTIFY_CHANNEL_ID = autosign["channel_id"]