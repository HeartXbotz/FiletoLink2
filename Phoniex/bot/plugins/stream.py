import os
import asyncio
from Script import script
from asyncio import TimeoutError
from Phoniex.bot import StreamBot
from Phoniex.utils.database import Database
from Phoniex.utils.human_readable import humanbytes
from Phoniex.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from shortzy import Shortzy

from Phoniex.utils.file_properties import get_name, get_hash, get_media_file_size

db = Database(Var.DATABASE_URL, Var.name)

MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")


@StreamBot.on_message(filters.group & filters.command("set_caption"))
async def add_caption(c: Client, m: Message):
    if len(m.command) == 1:
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        return await m.reply_text(
            "**ʜᴇʏ 👋\n\n<u>ɢɪᴠᴇ ᴛʜᴇ ᴄᴀᴩᴛɪᴏɴ</u>\n\n"
            "ᴇxᴀᴍᴩʟᴇ:- `/set_caption <b>{file_name}\n\n"
            "Size : {file_size}\n\n➠ Fast Download Link :\n"
            "{download_link}\n\n➠ Watch Download Link : {watch_link}</b>`**",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    caption = m.text.split(" ", 1)[1]
    
    # Store caption for the group
    await db.set_caption(m.chat.id, caption=caption)

    buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
    
    await m.reply_text(
        f"<b>ʜᴇʏ {m.from_user.mention}\n\n✅ Caption added and saved successfully!</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@StreamBot.on_message(filters.group & filters.command("del_caption"))
async def delete_caption(c: Client, m: Message):
    caption = await db.get_caption(m.chat.id)
    
    if not caption:
        return await m.reply_text("__**😔 No caption found in this group.**__")
    
    await db.set_caption(m.chat.id, caption="")  # Delete caption for the group
    
    buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
    
    await m.reply_text(
        f"<b>ʜᴇʏ {m.from_user.mention}\n\n✅ Caption deleted successfully.</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@StreamBot.on_message(filters.group & filters.command(["see_caption", "view_caption"]))
async def see_caption(c: Client, m: Message):
    caption = await db.get_caption(m.chat.id)
    buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
    if caption:
        await m.reply_text(
            f"**Group Caption:**\n\n<b>{caption}</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await m.reply_text(
            "__**😔 No caption set for this group.**__",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


@StreamBot.on_message(filters.group & (filters.document | filters.video | filters.audio), group=4)
async def private_receive_handler(c: Client, m: Message):
    if m.chat.id not in Var.GROUP_ID:
        return

    media = m.document or m.video or m.audio
    if not media:
        return  

    file_name = m.caption.split('\n')[0] if m.caption else "Untitled File"
    file_name = file_name.replace(".mkv", "").replace("HEVC", "#HEVC").replace("Sample video.", "#SampleVideo")
    
    try:
        user = await db.get_user(m.from_user.id)
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)

        hs_stream_link = f"{Var.URL}exclusive/{log_msg.id}/?hash={get_hash(log_msg)}"
        hs_online_link = f"{Var.URL}{log_msg.id}/?hash={get_hash(log_msg)}"

        stream_link = await short_link(hs_stream_link, user)
        online_link = await short_link(hs_online_link, user)

        await log_msg.reply_text(
            text=(
                f"**Requested by :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n"
                f"**User ID :** `{m.from_user.id}`\n"
                f"**Stream Link :** {stream_link}"
            ),
            disable_web_page_preview=True,
            quote=True,
        )

        default_caption = (
            "<b>📂 File Name : {file_name}\n\n"
            "📦 File Size : {file_size}\n\n"
            "📥 Fast Download Link :\n{download_link}\n\n"
            "🖥 Watch Download Link :\n{watch_link}</b>"
        )

        c_caption = await db.get_caption(m.chat.id)  # Fetch group caption
        caption_template = c_caption if c_caption else default_caption
        file_size = humanbytes(get_media_file_size(m) or 0)

        caption = caption_template.format(
            file_name=file_name,
            file_size=file_size,
            download_link=online_link or "No download link available",
            watch_link=stream_link or "No stream link available",
        )

        sent_message = await c.send_cached_media(
            caption=caption,
            chat_id=m.chat.id,
            file_id=media.file_id,
        )

        await asyncio.sleep(300)
        await sent_message.delete()

    except FloodWait as e:
        print(f"Sleeping for {e.x}s due to FloodWait")
        await asyncio.sleep(e.x)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=(
                f"Got FloodWait of {e.x}s from "
                f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n"
                f"**User ID :** `{m.from_user.id}`"
            ),
            disable_web_page_preview=True,
        )

async def short_link(link, user=None):
    if not user:
        return link

    api_key = user.get("shortner_api")
    base_site = user.get("shortner_url")

    if api_key and base_site and Var.USERS_CAN_USE:
        shortzy = Shortzy(api_key, base_site)
        link = await shortzy.convert(link)

    return link


@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video) & ~filters.forwarded, group=-1,)
async def channel_receive_handler(bot, message):
    file_name = message.caption.split('\n')[0] if message.caption else "Untitled File"
    
    try:
        log_msg = await message.forward(chat_id=Var.BIN_CHANNEL)
        streamxlink = f"{Var.URL}exclusive/{log_msg.id}/?hash={get_hash(log_msg)}"
        stream_link = await short_link(streamxlink)

        caption = (
            f"<b>@TamizhFiles {file_name}\n\n"
            f"➠ Fᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ Lɪɴᴋ:\n"
            f"╰┈➤ {stream_link}\n\n"
            f"♡꘎ 𓆩 Uᴘʟᴏᴀᴅᴇᴅ Bʏ: <a href='https://t.me/TamizhFiles'>Tamizh Files</a> 𓆪 ꘎♡</b>"
        )
        
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message.id, caption=caption)

    except FloodWait as e:
        await asyncio.sleep(e.x)
