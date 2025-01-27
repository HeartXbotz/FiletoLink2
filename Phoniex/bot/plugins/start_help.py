import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant

from Phoniex.bot import StreamBot
from Phoniex.vars import Var
from Phoniex.utils.database import Database
from Phoniex.utils.file_properties import get_name, get_hash, get_media_file_size
from Phoniex.utils.human_readable import humanbytes
from Phoniex.bot.plugins.stream import MY_PASS
from Script import script

# Setup logger
logger = logging.getLogger(__name__)

# Initialize database
db = Database(Var.DATABASE_URL, Var.name)

# Temporary user details for greeting
class TempUser:
    U_NAME = None
    B_NAME = None

# Function to check if user is subscribed to the required channel
async def not_subscribed(_, client, message):
    await db.hs_add_user(client, message)
    if not Var.FORCE_SUB:
        return False

    try:
        user = await client.get_chat_member(Var.FORCE_SUB, message.from_user.id)
        if user.status == enums.ChatMemberStatus.BANNED:
            return True
        else:
            return False
    except UserNotParticipant:
        pass
    return True

# Function to send subscription reminder message
@StreamBot.on_message(filters.group & filters.create(not_subscribed))
async def forces_sub(client, message):
    buttons = [
        [
            InlineKeyboardButton(
                text="🥀 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🥀", 
                url=f"https://t.me/{Var.FORCE_SUB}"
            )
        ]
    ]
    text = "**ʜᴇʏ {}\n\nsᴏʀʀʏ ᴅᴜᴅᴇ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴍʏ ᴄʜᴀɴɴᴇʟ 😐. sᴏ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴏᴜʀ ᴜᴩᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ**"
    try:
        user = await client.get_chat_member(Var.FORCE_SUB, message.from_user.id)
        if user.status == enums.ChatMemberStatus.BANNED:
            return await client.send_message(
                message.from_user.id, text="Sᴏʀʀʏ Yᴏᴜ'ʀᴇ Bᴀɴɴᴇᴅ Tᴏ Uꜱᴇ Mᴇ"
            )
    except UserNotParticipant:
        return await message.reply_text(
            text=text.format(message.from_user.mention, TempUser.U_NAME, TempUser.B_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    return await message.reply_text(
        text=text, reply_markup=InlineKeyboardMarkup(buttons)
    )

# Start command handler
@StreamBot.on_message(filters.command(["start"]) & filters.text & filters.incoming)
async def start(client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ 📌", url="https://t.me/+T5AZwVNnpLZmNTY1"
                    )
                ]
            ]
        )
        await db.hs_add_user(client, message)
        user_id = message.from_user.id

        # Handle report message
        if "report_" in message.text:
            _, message_id = message.text.split("_", 1)
            await client.send_message(
                chat_id=1032438381,
                text=f"""<b>New Report Has Been Registered
Reported by

User: <a href='tg://openmessage?user_id={user_id}'>1 View</a> | <a href='tg://user?id={user_id}'>2 View</a>

Reposted Message : 

<a href='https://t.me/c/1981587599/{message_id}'>View Message</a>
</b>""",
                parse_mode=enums.ParseMode.HTML,
            )
            await message.reply_text(
                text="<b>Report has been Registered..!\n\nAdmins will verify asap and remove the links and files.\n\nThanks for Reporting.</b>",
                disable_web_page_preview=True,
            )
        else:
            await message.reply_text(
                text=script.START_TXT.format(message.from_user.mention, TempUser.U_NAME, TempUser.B_NAME),
                disable_web_page_preview=True,
                reply_markup=keyboard,
            )
    elif message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Phoniex", url=f"https://t.me/Phoniex")]]
        )
        await db.hs_add_user(client, message)
        mr = await message.reply_text(
            f"<b>👋 ʜᴇʟʟᴏ {message.from_user.mention}!\n\nɪ» ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀꜰᴜʟʟ ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ ᴀɴᴅ ᴡᴀᴄᴛʜ ʟɪɴᴋ ʙᴏᴛ\n\n» ᴊᴏɪɴ ᴏᴜʀ ᴄʟᴏᴜᴅ ᴄʜᴀɴɴᴇʟ !!</b>",
            reply_markup=keyboard,
        )
        await asyncio.sleep(30)
        await mr.delete()
        await message.delete()

# Callback query handler
@StreamBot.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    user = query.from_user
    message = query.message

    if data == "start":
        await query.message.edit_text(
            text=(script.START_TXT.format(query.from_user.mention)),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ 📌", url="https://t.me/Phoniex"
                        )
                    ]
                ]
            ),
        )
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            await query.message.delete()

# Stats command handler
@StreamBot.on_message(filters.command("stats") & filters.incoming)
async def get_stats(bot, message):
    rju = await message.reply("<b>ᴀᴄᴄᴇssɪɴɢ sᴛᴀᴛᴜs ᴅᴇᴛᴀɪʟs...</b>")
    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
    await rju.edit_text(
        text=script.STATUS_TXT.format(total_users, total_chats),
        reply_markup=InlineKeyboardMarkup(buttons),
    )

# Shortener API handler
@StreamBot.on_message(filters.command("shortner_api") & filters.group)
async def shortner_api_handler(bot, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    api = user.get("shortner_api")
    cmd = m.command

    if len(cmd) == 1:
        text = f"<b>👋 ʜᴇʏ\n\nᴄᴜʀʀᴇɴᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ :\n<code>{api}</code>\n\nᴇx</b>:<code>/shortner_api 12345678848def53bf2d4e69608443cf27</code>\n\n<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ - <a href='https://t.me/Phoniex'>Phoniex</a></b>"
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        return await m.reply(
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
    elif len(cmd) == 2:
        api = cmd[1].strip()
        await db.update_user_info(user_id, {"shortner_api": api})
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        await m.reply(
            f"<b>sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ ᴜᴘᴅᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴛᴏ {api}</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

# Shortener URL handler
@StreamBot.on_message(filters.command("shortner_url") & filters.group)
async def shortner_url_handler(bot, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    cmd = m.command
    site = user.get("shortner_url")
    text = f"<b>👋 ʜᴇʏ\n\nᴄᴜʀʀᴇɴᴛ sʜᴛɴᴇʀ ᴜʀʟ :\n<code>{site}</code>\n\n ᴇx</b>: <code>/shortner_url tnshort.net</code>\n\n<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ - <a href='https://t.me/Phoniex'>Phoniex</a></b>"
    
    if len(cmd) == 1:
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        return await m.reply(
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
    elif len(cmd) == 2:
        shortner_url = cmd[1].strip()
        await db.update_user_info(user_id, {"shortner_url": shortner_url})
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        await m.reply(
            "<b>sʜᴏʀᴛɴᴇʀ ᴜʀʟ ᴜᴘᴅᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

@StreamBot.on_message(filters.command("remove_shortner_url") & filters.group)
async def remove_shortner(c, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    print(user)
    if user.get("shortner_url"):
        await db.update_user_info(user_id, {"shortner_url": None})
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        await m.reply(
            "<b>sʜᴏʀᴛᴇɴᴇʀ ᴜʀʟ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        await m.reply(
            "<b>ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ꜱʜᴏʀᴛᴇɴᴇʀ ᴜʀʟ</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
