with open("setup/config.yaml", "r") as file:
    import yaml
    config = yaml.safe_load(file)

with open("setup/autosign.yaml", "r") as file:
    import yaml
    autosign = yaml.safe_load(file)

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