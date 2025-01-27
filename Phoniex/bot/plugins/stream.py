import os
import asyncio
from urllib.parse import quote_plus

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from shortzy import Shortzy
from Phoniex.bot import StreamBot
from Phoniex.utils.database import Database
from Phoniex.utils.human_readable import humanbytes
from Phoniex.utils.file_properties import get_name, get_hash, get_media_file_size
from Phoniex.vars import Var

# Database instances
db = Database(Var.DATABASE_URL, Var.name)

# Global Variables
MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}


# Helper Function to Shorten Links
async def short_link(link, user=None):
    if not user:
        return link
    api_key = user.get("shortner_api")
    base_site = user.get("shortner_url")
    if api_key and base_site:
        shortzy = Shortzy(api_key, base_site)
        link = await shortzy.convert(link)
    return link


# Command: Set Caption
@StreamBot.on_message(filters.group & filters.command("set_caption"))
async def add_caption(client: Client, message: Message):
    if len(message.command) == 1:
        buttons = [[InlineKeyboardButton("⇇ Close ⇉", callback_data="close")]]
        return await message.reply_text(
            "**Hey 👋\n\n<u>Provide the caption</u>\n\nExample:**\n`/set_caption {file_name}\nSize: {file_size}\n➠ Download Link: {download_link}\n➠ Watch Link: {watch_link}`",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    caption = message.text.split(" ", 1)[1]
    await db.set_caption(message.from_user.id, caption=caption)
    buttons = [[InlineKeyboardButton("⇇ Close ⇉", callback_data="close")]]
    await message.reply_text(
        f"<b>Hey {message.from_user.mention}\n\n✅ Caption added successfully!</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# Command: Delete Caption
@StreamBot.on_message(filters.group & filters.command("del_caption"))
async def delete_caption(client: Client, message: Message):
    caption = await db.get_caption(message.from_user.id)
    if not caption:
        return await message.reply_text("😔 You don't have any caption set.")
    await db.set_caption(message.from_user.id, caption=None)
    buttons = [[InlineKeyboardButton("⇇ Close ⇉", callback_data="close")]]
    await message.reply_text(
        f"<b>Hey {message.from_user.mention}\n\n✅ Caption deleted successfully!</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# Command: View Caption
@StreamBot.on_message(filters.group & filters.command(["see_caption", "view_caption"]))
async def see_caption(client: Client, message: Message):
    caption = await db.get_caption(message.from_user.id)
    if caption:
        await message.reply_text(f"**Your caption:**\n\n`{caption}`")
    else:
        await message.reply_text("😔 You don't have any caption set.")


# Media Handler for Groups
@StreamBot.on_message(filters.group & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def media_handler(client: Client, message: Message):
    if message.chat.id not in Var.GROUP_ID:
        return

    media = message.document or message.video or message.audio
    if not media:
        return

    file_name = message.caption if message.caption else ""
    file_name = file_name.replace(".mkv", "").replace("HEVC", "#HEVC").replace("Sample video.", "#SampleVideo")

    log_msg = await message.forward(chat_id=Var.BIN_CHANNEL)

    hs_stream_link = f"{Var.URL}exclusive/{log_msg.id}/{quote_plus(get_name(log_msg))}?Phoniex={get_hash(log_msg)}"
    hs_online_link = f"{Var.URL}{log_msg.id}/{quote_plus(get_name(log_msg))}?Phoniex={get_hash(log_msg)}"

    user = await db.get_user(message.from_user.id)
    stream_link = await short_link(hs_stream_link, user)
    online_link = await short_link(hs_online_link, user)

    caption_template = """<b>📂 File Name: {file_name}\n📦 File Size: {file_size}\n📥 Download Link: {download_link}\n🖥 Watch Link: {watch_link}</b>"""
    c_caption = await db.get_caption(message.from_user.id)

    caption = c_caption.format(
        file_name=file_name,
        file_size=humanbytes(get_media_file_size(message)),
        download_link=online_link,
        watch_link=stream_link,
    ) if c_caption else caption_template.format(
        file_name=file_name,
        file_size=humanbytes(get_media_file_size(message)),
        download_link=online_link,
        watch_link=stream_link,
    )

    try:
        await client.send_cached_media(chat_id=message.chat.id, file_id=media.file_id, caption=caption)
    except FloodWait as e:
        print(f"FloodWait: Sleeping for {e.x}s")
        await asyncio.sleep(e.x)


# Channel Media Handler
@StreamBot.on_message(filters.channel & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1)
async def channel_handler(client: Client, message: Message):
    media = message.document or message.video or message.audio
    if not media:
        return

    file_name = message.caption if message.caption else ""
    replacements = {
        ".mkv": "",
        "Uploaded by @Phoniex": "",
        "HEVC": "#HEVC",
        "Sample video.": "#SampleVideo",
    }
    for old, new in replacements.items():
        file_name = file_name.replace(old, new)

    log_msg = await message.forward(chat_id=Var.BIN_CHANNEL)

    hs_stream_link = f"{Var.URL}exclusive/{log_msg.id}/?Phoniex={get_hash(log_msg)}"
    stream_link = await short_link(hs_stream_link)
    hs_online_link = f"{Var.URL}{log_msg.id}/?Phoniex={get_hash(log_msg)}"
    online_link = await short_link(hs_online_link)

    caption = (
        f"<b>@PhoniexFiles {file_name}\n\n"
        f"🗳 Download Link: {stream_link}\n\n"
        f"⚜️ Uploaded by <a href='https://t.me/PhoniexFiles'><b>PhoniexFiles</b></a></b>"
    )

    try:
        await client.send_cached_media(chat_id=message.chat.id, file_id=media.file_id, caption=caption)
        await message.delete()
    except Exception as e:
        print(f"Error: {e}")
