import sys
import glob
import asyncio
import logging
import importlib
from pathlib import Path
from pyrogram import idle
from aiohttp import web
from Phoniex.bot import StreamBot
from Phoniex.vars import Var
from Phoniex.server import web_server
from Phoniex.utils.keepalive import ping_server
from Phoniex.bot.clients import initialize_clients

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

ppath = "Phoniex/bot/plugins/*.py"
files = glob.glob(ppath)

loop = asyncio.get_event_loop()


async def start_services():
    print("\n")
    print("------------------- Initializing Telegram Bot -------------------")
    try:
        await StreamBot.start()
        bot_info = await StreamBot.get_me()
        StreamBot.username = bot_info.username
        print(f"Bot Started Successfully! Username: {StreamBot.username}")
    except Exception as e:
        print(f"Error starting bot: {e}")
        return

    print("---------------------- Initializing Clients ----------------------")
    await initialize_clients()
    print("------------------------------ DONE ------------------------------")

    print("\n--------------------------- Importing Plugins ---------------------------")
    for name in files:
        try:
            with open(name) as a:
                patt = Path(a.name)
                plugin_name = patt.stem.replace(".py", "")
                plugins_dir = Path(f"Phoniex/bot/plugins/{plugin_name}.py")
                import_path = f"Phoniex.bot.plugins.{plugin_name}"
                spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
                load = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(load)
                sys.modules[import_path] = load
                print(f"✅ Imported Plugin: {plugin_name}")
        except Exception as e:
            print(f"❌ Failed to import {plugin_name}: {e}")

    print("------------------ Starting Keep Alive Service ------------------")
    asyncio.create_task(ping_server())

    print("-------------------- Initializing Web Server --------------------")
    try:
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = Var.BIND_ADRESS
        await web.TCPSite(app, bind_address, Var.PORT).start()
        print(f"✅ Web Server Running on {bind_address}:{Var.PORT}")
    except Exception as e:
        print(f"❌ Web Server Error: {e}")

    print("\n----------------------- Service Started --------------------------")
    print(f"Bot: {bot_info.first_name} (@{bot_info.username})")
    print(f"Server IP: {bind_address}:{Var.PORT}")
    print(f"Owner: {Var.OWNER_USERNAME}")
    print("------------------------------------------------------------------")

    await idle()  # Keep the bot running


if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info("----------------------- Service Stopped -----------------------")
