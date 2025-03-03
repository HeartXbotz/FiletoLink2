import os
import aiohttp
import asyncio
from Script import script
from asyncio import TimeoutError
from Phoniex.bot import StreamBot
from Phoniex.utils.database import Database
from Phoniex.utils.human_readable import humanbytes
from Phoniex.vars import Var
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from shortzy import Shortzy
from pyrogram import errors
from pyrogram.errors import FloodWait
from Phoniex.utils.file_properties import get_name, get_hash, get_media_file_size


db = Database(Var.DATABASE_URL, Var.name)


MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")


class temp(object):
    U_NAME = None
    B_NAME = None


@StreamBot.on_message(
    filters.group & (filters.document | filters.video | filters.audio | filters.photo),
    group=4
)
async def private_receive_handler(c: Client, m: Message):
    """Handles media in groups and generates links."""

    if str(m.chat.id).startswith("-100") and m.chat.id not in Var.GROUP_ID:
        return
    elif m.chat.id not in Var.GROUP_ID:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id)
            await c.send_message(
                Var.BIN_CHANNEL,
                f"New User Joined! : \n\n Name : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!!",
            )
            return

    media = m.document or m.video or m.audio or m.photo
    if not media:
        return

    # ✅ Auto-detect caption
    file_name = m.caption if m.caption else media.file_name or ""

    # ✅ Clean filename
    replacements = {
        ".mkv": "",
        "HEVC": "#HEVC",
        "Sample video.": "#SampleVideo",
    }
    for old, new in replacements.items():
        file_name = file_name.replace(old, new)

    try:
        user = await db.get_user(m.from_user.id)
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)

        # ✅ Generate stream & download links
        hs_stream_link = f"{Var.URL}exclusive/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        stream_link = await short_link(hs_stream_link, user)

        hs_online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = await short_link(hs_online_link, user)

        # ✅ Log request details
        await log_msg.reply_text(
            text=(
                f"**Requested by:** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n"
                f"**User ID:** `{m.from_user.id}`\n"
                f"**Stream Link:** {stream_link}"
            ),
            disable_web_page_preview=True,
            quote=True,
        )

        # ✅ Custom caption handling with Debugging
        c_caption = await db.get_caption(m.from_user.id)
        print(f"DEBUG: Retrieved Caption -> {c_caption}")  # Debugging

        if c_caption:
            try:
                caption = c_caption.format(
                    file_name=file_name,
                    file_size=humanbytes(get_media_file_size(m)),
                    download_link=online_link,
                    watch_link=stream_link,
                )
            except KeyError as e:
                print(f"Caption formatting error: Missing key {e}")
                caption = None  # Use a fallback caption
            except Exception as e:
                print(f"Caption formatting error: {e}")
                caption = None
        else:
            caption = (
                f"<b>📂 File Name: {file_name}\n\n"
                f"📦 File Size: {humanbytes(get_media_file_size(m))}\n\n"
                f"📥 Fast Download Link:\n{online_link}\n\n"
                f"🖥 Watch Link:\n{stream_link}</b>"
            )

        # ✅ Send media with caption
        if caption:
            await c.send_cached_media(
                caption=caption, chat_id=m.chat.id, file_id=media.file_id
            )
        else:
            print("DEBUG: Caption was None, using default caption.")  # Debugging
            await c.send_cached_media(
                caption="⚠️ Caption formatting failed. Using default.", 
                chat_id=m.chat.id, 
                file_id=media.file_id
            )

    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=(
                f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n"
                f"**User ID:** `{str(m.from_user.id)}`"
            ),
            disable_web_page_preview=True,
        )


async def short_link(link, user=None):
    """Shortens links using user-specific settings."""
    if not user:
        return link

    api_key = user.get("shortner_api")
    base_site = user.get("shortner_url")

    if api_key and base_site and Var.USERS_CAN_USE:
        shortzy = Shortzy(api_key, base_site)
        link = await shortzy.convert(link)

    return link


@StreamBot.on_message(
    filters.channel & ~filters.group & (filters.document | filters.video | filters.photo) & ~filters.forwarded,
    group=-1,
)
async def channel_receive_handler(bot, broadcast):
    """Handles media from channels and generates links."""
    try:
        message_id = broadcast.id
        chat_id = broadcast.chat.id
        media = broadcast.document or broadcast.video or broadcast.audio

        # ✅ Extract caption if available
        file_name = broadcast.caption if media else ""
        
        # ✅ Clean filename (remove unnecessary parts)
        replacements = {
            ".mkv": "",
            "〽️ Uploaded by @heartxbotz": "",
            "HEVC": "#HEVC",
            "Sample video.": "#SampleVideo",
        }
        for old, new in replacements.items():
            file_name = file_name.replace(old, new)

        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)

        # ✅ Generate Stream & Download Links
        hs_stream_link = f"{Var.URL}exclusive/{str(log_msg.id)}/?hash={get_hash(log_msg)}"
        stream_link = await short_link(hs_stream_link, await db.get_user(broadcast.sender_chat.id))

        hs_online_link = f"{Var.URL}{str(log_msg.id)}/?hash={get_hash(log_msg)}"
        online_link = await short_link(hs_online_link, await db.get_user(broadcast.sender_chat.id))

        # ✅ Format the caption properly
        caption = (
            f"<b>{file_name}</b>\n"
            f"🗳 Fast Stream Link: <a href='{stream_link}'>DOWNLOAD 🚀</a>\n\n"
            f"〽️ Uploaded by @HeartxBotz"
        )

        # ✅ Send media with caption
        await bot.send_cached_media(
            caption=caption, chat_id=chat_id, file_id=media.file_id
        )

        await broadcast.delete()

    except Exception as e:
        print(f"Error: {e}")
        print(f"Original message ID: {message_id}")
        print(f"Chat ID: {chat_id}")
        print(f"Forwarded message ID: {log_msg.id}")
        print(f"hs_stream_link: {hs_stream_link}")
        print(f"stream_link: {stream_link}")
        print(f"hs_online_link: {hs_online_link}")
        print(f"online_link: {online_link}")
