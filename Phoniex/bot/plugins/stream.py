hs_online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?Phoniex={get_hash(log_msg)}"
        online_link = await short_link(hs_online_link, user)

        msg_text ="""<b>📂 ғɪʟᴇ ɴᴀᴍᴇ : {file_name}\n\n📦 ғɪʟᴇ ꜱɪᴢᴇ : {file_size}\n\n📥 ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ :\n{download_link}\n\n🖥 ᴡᴀᴛᴄʜ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ  :\n{watch_link}</b>"""

        await log_msg.reply_text(
            text=f"RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ : [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nUꜱᴇʀ ɪᴅ : {m.from_user.id}\nStream ʟɪɴᴋ : {stream_link}",
            disable_web_page_preview=True,
            quote=True,
        )
        c_caption = await db.get_caption(m.from_user.id)
        if c_caption:
            try:
                caption = c_caption.format(
                    file_name="" if file_name is None else file_name,
                    file_size=humanbytes(get_media_file_size(m)),
                    download_link=online_link,
                    watch_link=stream_link,
                )
            except Exception as e:
                #return
            else:
                caption = caption.format(
                    file_name="" if file_name is None else file_name,
                    file_size=humanbytes(get_media_file_size(m)),
                    download_link=online_link,
                    watch_link=stream_link,
                )
        await c.send_cached_media(
            caption=caption, chat_id=m.chat.id, file_id=media.file_id
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n𝚄𝚜𝚎𝚛 𝙸𝙳 : {str(m.from_user.id)}",
            disable_web_page_preview=True,
        )


async def short_link(link, user=None):
    if not user:
        return link

    api_key = user.get("shortner_api")
    base_site = user.get("shortner_url")

    if bool(api_key and base_site) and Var.USERS_CAN_USE:
        shortzy = Shortzy(api_key, base_site)
        link = await shortzy.convert(link)

    return link


 await c.send_cached_media(
            caption=caption,
            chat_id=-1002480489590,
            file_id=media.file_id
         )


async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link


@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1,)
async def channel_receive_handler(bot, broadcast):
    try:
        message_id = broadcast.id
        chat_id = broadcast.chat.id
        media = broadcast.document or broadcast.video or broadcast.audio

        file_name = (
            broadcast.caption
            if (broadcast.document or broadcast.video or broadcast.audio)
            else ""
        )

        replacements = {
            ".mkv": "",
            "Uploaded by @Phoniex": "",
            "HEVC": "#HEVC",
            "Sample video.": "#SampleVideo",
        }

        for old, new in replacements.items():
            file_name = file_name.replace(old, new)

        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)

        hs_stream_link = (
            f"{Var.URL}exclusive/{str(log_msg.id)}/?Phoniex={get_hash(log_msg)}"
        )
        stream_link = await get_shortlink(
            Var.SHORTLINK_URL2, Var.SHORTLINK_API2, hs_stream_link
        )

        hs_online_link = f"{Var.URL}{str(log_msg.id)}/?MadxMoviez={get_hash(log_msg)}"
        online_link = await get_shortlink(
            Var.SHORTLINK_URL2, Var.SHORTLINK_API2, hs_online_link
        )

        caption = (
            f"<b>@TamizhFiles {file_name}"
            f"🗳 Fast Stream Link : <a href='{stream_link}'>DOWNLOAD 🚀</a>\n\n"
            f" Uploaded by @Phoniex</b>"
        )
        await bot.send_cached_media(
            caption=caption, chat_id=chat_id, file_id=media.file_id
        )
        await broadcast.delete()

    except Exception as e:
        print(f"Error : {e}")
        print(f"Original message ID: {message_id}")
        print(f"Chat ID: {chat_id}")
        print(f"Forwarded message ID: {log_msg.id}")
        print(f"hs_stream_link: {hs_stream_link}")
        print(f"stream_link: {stream_link}")
        print(f"hs_online_link: {hs_online_link}")
        print(f"online_link: {online_link}")
