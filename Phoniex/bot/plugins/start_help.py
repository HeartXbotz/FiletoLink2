from Phoniex.bot import StreamBot
from Phoniex.vars import Var
import logging, asyncio

logger = logging.getLogger(__name__)
from Phoniex.bot.plugins.stream import MY_PASS
from Phoniex.utils.human_readable import humanbytes
from Phoniex.utils.database import Database
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant
from Phoniex.utils.file_properties import get_name, get_hash, get_media_file_size

db = Database(Var.DATABASE_URL, Var.name)
from pyrogram.types import ReplyKeyboardMarkup


class temp(object):
    U_NAME = None
    B_NAME = None


@StreamBot.on_message(filters.command(["start"]) & filters.text & filters.incoming)
async def start(client, message):
    await db.hs_add_user(client, message)  # Ensure user is added to the database

    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ 📌", url="https://t.me/FileConvertLink")]]
    )

    if message.chat.type == enums.ChatType.PRIVATE:
        if "report_" in message.text:
            _, message_id = message.text.split("_", 1)
            await client.send_message(
                chat_id=1032438381,
                text=f"""<b>New Report Has Been Registered
Reported by:

User: <a href='tg://openmessage?user_id={user_id}'>1 View</a> | <a href='tg://user?id={user_id}'>2 View</a>

Reposted Message: 

<a href='https://t.me/c/1981587599/{message_id}'>View Message</a>
</b>""",
                parse_mode=enums.ParseMode.HTML,
            )
            await message.reply_text(
                text="<b>Report has been Registered..!\n\nAdmins will verify ASAP and remove the links/files.\n\nThanks for Reporting.</b>",
                disable_web_page_preview=True,
            )
        else:
            await message.reply_text(
                text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
                disable_web_page_preview=True,
                reply_markup=keyboard,
            )

    elif message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("HeartxBotz", url="https://t.me/heartxbotz")]]
        )

        msg = await message.reply_text(
            f"<b>👋 ʜᴇʟʟᴏ {message.from_user.mention}!\n\nI am a powerful and fast download & watch link bot.\n\nJoin our cloud channel!</b>",
            reply_markup=group_keyboard,
        )
        await asyncio.sleep(30)
        await msg.delete()
        await message.delete()


@StreamBot.on_message(filters.command("commands") & filters.group)
async def about_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started !!",
        )
    hs = await message.reply_photo(
        photo="https://envs.sh/bKP.jpg",
        caption=(script.COMMENTS_TXT.format(message.from_user.mention)),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        ),
    )
    await asyncio.sleep(20)
    await hs.delete()
    await message.delete()


@StreamBot.on_message(filters.command("stats") & filters.incoming)
async def get_ststs(bot, message):
    rju = await message.reply("<b>ᴀᴄᴄᴇssɪɴɢ sᴛᴀᴛᴜs ᴅᴇᴛᴀɪʟs...</b>")
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
    await rju.edit_text(
        text=script.STATUS_TXT.format(total_users, totl_chats),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@StreamBot.on_message(filters.command("shortner_api") & filters.group)
async def shortner_api_handler(bot, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    api = user.get("shortner_api")
    cmd = m.command
    if len(cmd) == 1:
        text = f"<b>👋 ʜᴇʏ\n\nᴄᴜʀʀᴇɴᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ :\n<code>{api}</code>\n\nᴇx</b>:<code>/shortner_api 12345678848def53bf2d4e69608443cf27</code>\n\n<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ - <a href='https://t.me/heartxbotz'>Heartxbotz</a></b>"
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


@StreamBot.on_message(filters.command("shortner_url") & filters.group)
async def shortner_url_handler(bot, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    cmd = m.command
    site = user.get("shortner_url")
    text = f"<b>👋 ʜᴇʏ\n\nᴄᴜʀʀᴇɴᴛ sʜʀᴛɴᴇʀ ᴜʀʟ :\n<code>{site}</code>\n\n ᴇx</b>: <code>/shortner_url tnshort.net</code>\n\n<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ - <a href='https://t.me/MadxBotz'>heartxBotz</a></b>"
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


@StreamBot.on_message(filters.command("remove_shortener_api") & filters.group)
async def remove_shortener(c, m):
    user_id = m.from_user.id
    user = await db.get_user(user_id)
    if user.get("shortner_api"):
        await db.update_user_info(user_id, {"shortner_api": None})
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        await m.reply(
            "<b>sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        await m.reply(
            "<b>ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ꜱʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ</b>",
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
