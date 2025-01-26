import os
import asyncio
from urllib.parse import quote_plus

from pyrogram import filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from Phoniex.bot import StreamBot
from Phoniex.utils.database import Database
from Phoniex.utils.human_readable import humanbytes
from Phoniex.utils.file_properties import get_name, get_hash, get_media_file_size
from shortzy import Shortzy
from Phoniex.vars import Var

# Initialize databases
db = Database(Var.DATABASE_URL, "captions")
pass_db = Database(Var.DATABASE_URL, "passwords")

# Placeholder for temp class
class temp(object):
    U_NAME = None
    B_NAME = None


@StreamBot.on_message(filters.group & filters.command("set_caption"))
async def add_caption(c: Client, m: Message):
    if len(m.command) == 1:
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        return await m.reply_text(
            "**ʜᴇʏ 👋\n\n<u>ɢɪᴠᴇ ᴛʜᴇ ᴄᴀᴩᴛɪᴏɴ</u>\n\n"
            "ᴇxᴀᴍᴩʟᴇ:- `/set_caption <b>{file_name}\n\nSize : {file_size}\n\n"
            "➠ Fast Download Link :\n{download_link}\n\n➠ Watch Link : {watch_link}</b>`**",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    caption = m.text.split(" ", 1)[1]
    await db.set_caption(m.from_user.id, caption=caption)
    buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
    await m.reply_text(
        f"<b>ʜᴇʏ {m.from_user.mention}\n\n✅ Caption saved successfully!</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@StreamBot.on_message(filters.group & filters.command("del_caption"))
async def delete_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)
    if not caption:
        return await m.reply_text("__**😔 You don't have any caption to delete.**__")
    await db.set_caption(m.from_user.id, caption=None)
    buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
    await m.reply_text(
        f"<b>ʜᴇʏ {m.from_user.mention}\n\n✅ Your caption has been deleted successfully.</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@StreamBot.on_message(filters.group & filters.command(["see_caption", "view_caption"]))
async def see_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)
    if caption:
        await m.reply_text(f"**Your saved caption:**\n\n`{caption}`")
    else:
        await m.reply_text("__**😔 You don't have any saved caption.**__")


@StreamBot.on_message(
    filters.group & (filters.document | filters.video | filters.audio | filters.photo),
    group=4,
)
async def private_receive_handler(c: Client, m: Message):
    if str(m.chat.id).startswith("-100") and m.chat.id not in Var.GROUP_ID:
        return

    media = m.document or m.video or m.audio or m.photo
    file_name = get_name(media) if media else ""
    file_name = file_name.replace(".mkv", "").replace("HEVC", "#HEVC").replace(
        "Sample video.", "#SampleVideo"
    )

    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}exclusive/{log_msg.id}/{quote_plus(get_name(log_msg))}?Phoniex={get_hash(log_msg)}"
        short_stream_link = await short_link(stream_link)

        online_link = f"{Var.URL}{log_msg.id}/{quote_plus(get_name(log_msg))}?Phoniex={get_hash(log_msg)}"
        short_online_link = await short_link(online_link)

        c_caption = await db.get_caption(m.from_user.id)
        caption = (
            c_caption.format(
                file_name=file_name,
                file_size=humanbytes(get_media_file_size(media)),
                download_link=short_online_link,
                watch_link=short_stream_link,
            )
            if c_caption
            else f"<b>📂 File Name: {file_name}\n\n📦 File Size: {humanbytes(get_media_file_size(media))}\n\n"
            f"📥 Fast Download Link: {short_online_link}\n\n🖥 Watch Link: {short_stream_link}</b>"
        )

        await c.send_cached_media(
            chat_id=m.chat.id, file_id=media.file_id, caption=caption
        )

    except FloodWait as e:
        print(f"FloodWait: Sleeping for {e.x} seconds")
        await asyncio.sleep(e.x)
    except Exception as e:
        print(f"Error: {e}")


async def short_link(link):
    try:
        shortzy = Shortzy(Var.SHORTLINK_API, Var.SHORTLINK_URL)
        return await shortzy.convert(link)
    except Exception:
        return link


@StreamBot.on_message(
    filters.channel
    & ~filters.group
    & (filters.document | filters.video | filters.photo)
    & ~filters.forwarded,
    group=-1,
)
async def channel_receive_handler(bot, broadcast):
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        file_name = get_name(broadcast.document or broadcast.video or broadcast.audio)

        stream_link = f"{Var.URL}exclusive/{log_msg.id}/{quote_plus(file_name)}?Phoniex={get_hash(log_msg)}"
        short_stream_link = await short_link(stream_link)

        caption = (
            f"<b>@TamizhFiles {file_name}\n\n"
            f"🗳 Fast Stream Link: <a href='{short_stream_link}'>DOWNLOAD 🚀</a>\n\n"
            f"Uploaded by @YourBotName</b>"
        )

        await bot.send_cached_media(
            chat_id=broadcast.chat.id,
            file_id=broadcast.document.file_id,
            caption=caption,
        )
        await broadcast.delete()

    except Exception as e:
        print(f"Error: {e}")
