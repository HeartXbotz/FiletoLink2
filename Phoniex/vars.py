import os, re
from os import getenv, environ
from dotenv import load_dotenv

id_pattern = re.compile(r"^.\d+$")


load_dotenv()


class Var(object):
    MULTI_CLIENT = False
    API_ID = int(getenv("API_ID", "22977776"))
    API_HASH = str(getenv("API_HASH", "2ac7223d720bdeec757cbc88ced57224"))
    BOT_TOKEN = str(getenv("BOT_TOKEN", "7870220937:AAHKH5QJYqtpGTZuNpx7qOPVvUpwBgVy-aE"))
    name = str(getenv("name", "filetolinkbot"))
    SLEEP_THRESHOLD = int(getenv("SLEEP_THRESHOLD", "60"))
    WORKERS = int(getenv("WORKERS", "200"))
    CUSTOM_FILE_CAPTION = environ.get(
        "CUSTOM_FILE_CAPTION", "<b>ɴᴀᴍᴇ : {file_name}\n\nꜱɪᴢᴇ : {file_size}</b>"
    )
    BIN_CHANNEL = int(getenv("BIN_CHANNEL", "-1002069400808"))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002069400808"))
    PERMANENT_GROUP = os.environ.get("PERMANENT_GROUP", "-1002069400808")

    CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002069400808"))

    GROUP_ID = [
        int(ch) for ch in (os.environ.get("GROUP_ID", f"{PERMANENT_GROUP}")).split()
    ]
    SHORTLINK_URL1 = os.environ.get("SHORTLINK_URL1", "Modijiurl.com")
    SHORTLINK_API1 = os.environ.get(
        "SHORTLINK_API1", "69bfe45fc35b6b3178b4b95de9ef1db14a746ce7"
    )

    SHORTLINK_URL2 = os.environ.get("SHORTLINK_URL2", "Modijiurl.com")
    SHORTLINK_API2 = os.environ.get(
        "SHORTLINK_API2", "69bfe45fc35b6b3178b4b95de9ef1db14a746ce7"
    )
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1002391269521"))
    FORCE_SUB = os.environ.get("FORCE_SUB", "-1002159407577")
    PORT = int(getenv("PORT", "8080"))
    BIND_ADRESS = str(getenv("WEB_SERVER_BIND_ADDRESS", "0.0.0.0"))
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
    ADMIN = [
        int(admin) if id_pattern.search(admin) else admin
        for admin in os.environ.get("ADMIN", "6762558871").split()
    ]
    OWNER_ID = set(int(x) for x in os.environ.get("OWNER_ID", "6762558871").split())
    NO_PORT = bool(getenv("NO_PORT", False))
    
    APP_NAME = str(getenv("APP_NAME", "f2l.botsfilesharing.workers.dev"))
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
            "mongodb+srv://jeevanantham8157:1055221@file2link.dhriy.mongodb.net/?retryWrites=true&w=majority&appName=File2Link",
        )
    )
    UPDATES_CHANNEL = str(getenv("UPDATES_CHANNEL", "None"))
    BANNED_CHANNELS = list(
        set(int(x) for x in str(getenv("BANNED_CHANNELS", "-1002431206698")).split())
    )
