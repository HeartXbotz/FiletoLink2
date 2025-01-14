import os, re
from os import getenv, environ
from dotenv import load_dotenv

id_pattern = re.compile(r"^.\d+$")


load_dotenv()


class Var(object):
    MULTI_CLIENT = False
    API_ID = int(getenv("API_ID", "28455032"))
    API_HASH = str(getenv("API_HASH", "28dbb18229d7701a856c42a46083cccf"))
    BOT_TOKEN = str(getenv("BOT_TOKEN", "8113792646:AAFl13NeYm-O5uqMB0EAkK81o6DynfOus6w"))
    name = str(getenv("name", "filetolinkbot"))
    SLEEP_THRESHOLD = int(getenv("SLEEP_THRESHOLD", "60"))
    WORKERS = int(getenv("WORKERS", "200"))
    CUSTOM_FILE_CAPTION = environ.get(
        "CUSTOM_FILE_CAPTION", "<b>ɴᴀᴍᴇ : {file_name}\n\nꜱɪᴢᴇ : {file_size}</b>"
    )
    BIN_CHANNEL = int(getenv("BIN_CHANNEL", "-1002087362405"))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001692749899"))
    PERMANENT_GROUP = os.environ.get("PERMANENT_GROUP", "-1002087362405")

    CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002087362405"))

    GROUP_ID = [
        int(ch) for ch in (os.environ.get("GROUP_ID", f"{PERMANENT_GROUP}")).split()
    ]
    SHORTLINK_URL1 = os.environ.get("SHORTLINK_URL1", "modijiurl.com")
    SHORTLINK_API1 = os.environ.get(
        "SHORTLINK_API1", "1bc9fe7b87fd246a19d0e5b10be262607b79ee89"
    )

    SHORTLINK_URL2 = os.environ.get("SHORTLINK_URL2", "modijiurl.com")
    SHORTLINK_API2 = os.environ.get(
        "SHORTLINK_API2", "1bc9fe7b87fd246a19d0e5b10be262607b79ee89"
    )
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1001692749899"))
    FORCE_SUB = os.environ.get("FORCE_SUB", "-1002400430988")
    PORT = int(getenv("PORT", "8080"))
    BIND_ADRESS = str(getenv("WEB_SERVER_BIND_ADDRESS", "0.0.0.0"))
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
    ADMIN = [
        int(admin) if id_pattern.search(admin) else admin
        for admin in os.environ.get("ADMIN", "1572929036").split()
    ]
    OWNER_ID = set(int(x) for x in os.environ.get("OWNER_ID", "1572929036").split())
    NO_PORT = bool(getenv("NO_PORT", False))
    
    APP_NAME = str(getenv("APP_NAME", "kuttycloud.filestorebots.workers.dev"))
    OWNER_USERNAME = str(getenv("OWNER_USERNAME", "@Itzz_Kutty"))
    BOT_USERNAME = str(getenv("BOT_USERNAME", "KuttyF2LBot"))
    

    DOMAIN = os.environ.get("DOMAIN", "https://kuttycloud.filestorebots.workers.dev")

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
    UPDATES_CHANNEL = str(getenv("UPDATES_CHANNEL", "None"))
    BANNED_CHANNELS = list(
        set(int(x) for x in str(getenv("BANNED_CHANNELS", "-1002247667952")).split())
    )
