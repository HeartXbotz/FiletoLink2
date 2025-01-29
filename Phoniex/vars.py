import os, re
from os import getenv, environ
from dotenv import load_dotenv

id_pattern = re.compile(r"^.\d+$")


load_dotenv()


class Var(object):
    MULTI_CLIENT = True
    API_ID = int(getenv("API_ID", "22977776"))
    API_HASH = str(getenv("API_HASH", "2ac7223d720bdeec757cbc88ced57224"))
    BOT_TOKEN = str(getenv("BOT_TOKEN", "7150457796:AAExPARfX4GPaufHQHkSyZo9vkbBc9z2yuY"))
    name = str(getenv("name", "filetolinkbot"))
    SLEEP_THRESHOLD = int(getenv("SLEEP_THRESHOLD", "60"))
    WORKERS = int(getenv("WORKERS", "200"))
    CUSTOM_FILE_CAPTION = environ.get(
        "CUSTOM_FILE_CAPTION", "<b>ɴᴀᴍᴇ : {file_name}\n\nꜱɪᴢᴇ : {file_size}</b>"
    )
    BIN_CHANNEL = int(getenv("BIN_CHANNEL", "-1002303784930")) #File store channel files redirected to this channel 
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002391269521"))
    PERMANENT_GROUP = os.environ.get("PERMANENT_GROUP", "-1002480489590")

    CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002480489590"))

    GROUP_ID = [
        int(ch) for ch in (os.environ.get("GROUP_ID", f"{PERMANENT_GROUP}")).split()
    ]
    SHORTLINK_URL1 = os.environ.get("SHORTLINK_URL1", "krownlinks.com")
    SHORTLINK_API1 = os.environ.get(
        "SHORTLINK_API1", "09c3580894bb9225404c58fe672a9677dc9a04ff"
    )

    SHORTLINK_URL2 = os.environ.get("SHORTLINK_URL2", "krownlinks.com")
    SHORTLINK_API2 = os.environ.get(
        "SHORTLINK_API2", "09c3580894bb9225404c58fe672a9677dc9a04ff"
    )
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1002391269521"))
    FORCE_SUB = os.environ.get("FORCE_SUB", "-1002159407577")
    PORT = int(getenv("PORT", "8080"))
    BIND_ADRESS = str(getenv("WEB_SERVER_BIND_ADDRESS", "0.0.0.0"))
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
    ADMIN = [
        int(admin) if id_pattern.search(admin) else admin
        for admin in os.environ.get("ADMIN", "6762558871 1397269319").split()
    ]
    OWNER_ID = set(int(x) for x in os.environ.get("OWNER_ID", "6762558871 1397269319").split())
    NO_PORT = bool(getenv("NO_PORT", False))
    
    APP_NAME = str(getenv("APP_NAME", "phoneix.koyeb.app"))
    OWNER_USERNAME = str(getenv("OWNER_USERNAME", "@Heart_thieft"))
    BOT_USERNAME = str(getenv("BOT_USERNAME", "HeartxF2L_Bot"))
    

    DOMAIN = os.environ.get("DOMAIN", "https://f2l.botsfilesharing.workers.dev/")

    HAS_SSL = bool(getenv("HAS_SSL", True))
    if HAS_SSL:
        URL = f"https://{APP_NAME}/"
    else:
        URL = f"https://{APP_NAME}/"
        
    USERS_CAN_USE = getenv("USERS_CAN_USE", True)
    DATABASE_URL = str(
        getenv(
            "DATABASE_URL",
            "mongodb+srv://kutty2:15@kuttyscraper2.oxpjo.mongodb.net/?retryWrites=true&w=majority&appName=KuttyScraper2",
        )
    )
    UPDATES_CHANNEL = str(getenv("UPDATES_CHANNEL", "-1002205204150"))
    BANNED_CHANNELS = list(
        set(int(x) for x in str(getenv("BANNED_CHANNELS", "-1002303784930")).split())
    )
