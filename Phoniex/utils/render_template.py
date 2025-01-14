from Phoniex.vars import Var
from Phoniex.bot import StreamBot
from Phoniex.utils.human_readable import humanbytes
from Phoniex.utils.file_properties import get_file_ids
from Phoniex.server.exceptions import InvalidHash
import urllib.parse
import aiofiles
import logging
import aiohttp
import base64
from Phoniex.bot import StreamBot


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string


async def render_page(id, secure_hash):
    converted_id = id * abs(Var.CHANNEL_ID)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    filelink = f"{Var.DOMAIN}/?GET=ASHVER_{base64_string}"
    message_id = f"https://t.me/{Var.BOT_USERNAME}?start=report_{id}"

    file_data = await get_file_ids(StreamBot, int(Var.CHANNEL_ID), int(id))

    await StreamBot.send_message(Var.LOG_CHANNEL_ID, "New Streaming")

    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    src = urllib.parse.urljoin(Var.URL, f"{secure_hash}{str(id)}")
    file_size = None

    async with aiohttp.ClientSession() as s:
        async with s.get(src) as u:
            file_size = humanbytes(int(u.headers.get("Content-Length")))

    if str(file_data.mime_type.split("/")[0].strip()) == "video":
        async with aiofiles.open("Phoniex/template/req.html") as r:
            filename = file_data.file_name.replace("_", " ")
            filename = filename.replace("KuttyBots", "KuttyBots")
            heading = "KuttyBots | {}".format(filename)
            tag = file_data.mime_type.split("/")[0].strip()
            link = Var.URL
            html = (await r.read()).replace("tag", tag) % (
                heading,
                link,
                src,
                filename,
                file_size,
                filelink,
                message_id,
            )

    elif str(file_data.mime_type.split("/")[0].strip()) == "audio":
        async with aiofiles.open("Phoniex/template/req.html") as r:
            filename = file_data.file_name.replace("_", " ")
            filename = filename.replace("KuttyBots", "KuttyBots")
            heading = "KuttyBots | {}".format(filename)
            tag = file_data.mime_type.split("/")[0].strip()
            link = Var.URL
            html = (await r.read()).replace("tag", tag) % (
                heading,
                link,
                src,
                filename,
                file_size,
                filelink,
                message_id,
            )

    else:
        async with aiofiles.open("Phoniex/template/dl.html") as r:
            filename = file_data.file_name.replace("_", " ")
            filename = filename.replace("KuttyBots", "KuttyBots")
            heading = "KuttyBots | {}".format(filename)
            html = (await r.read()) % (heading, filename, src, file_size)

    return html
