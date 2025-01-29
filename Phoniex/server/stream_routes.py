import re
import time
import math
import logging
import secrets
import mimetypes
from aiohttp import web
import aiofiles, jinja2
from aiohttp.http_exceptions import BadStatusLine
from Phoniex.bot import multi_clients, work_loads, StreamBot
from Phoniex.server.exceptions import FIleNotFound, InvalidHash
from Phoniex import StartTime, __version__
from ..utils.time_format import get_readable_time
from ..utils.custom_dl import ByteStreamer
from Phoniex.utils.render_template import render_page
from Phoniex.vars import Var

routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root_route_handler(_):
    html_content = await render_template(
        "index.html",
        {
            "server_status": "running",
            "uptime": get_readable_time(time.time() - StartTime),
            "telegram_bot": "@" + StreamBot.username,
            "connected_bots": len(multi_clients),
            "loads": dict(
                ("Bot " + str(c + 1), l)
                for c, (_, l) in enumerate(
                    sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
                )
            ),
            "version": __version__,
            "headlink": "Phoniex.live",
        },
    )

    return web.Response(body=html_content, content_type="text/html")


async def render_template(template_name, context):
    template_dir = "Phoniex/template"

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

    template = env.get_template(template_name)

    html_content = template.render(context)

    return html_content


@routes.get(r"/exclusive/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")

        return web.Response(
            text=await render_page(id, secure_hash), content_type="text/html"
        )
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))


@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))


class_cache = {}


async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get(
        "Range", None
    )  # Get the range header, None if not present

    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]

    if Var.MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote}")

    # Fetch ByteStreamer object, use cached or create new
    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect

    try:
        logging.debug("before calling get_file_properties")
        file_id = await tg_connect.get_file_properties(id)
        logging.debug("after calling get_file_properties")
    except Exception as e:
        logging.error(f"Error fetching file properties: {e}")
        return web.Response(status=500, body="Error fetching file properties")

    # Check if the file hash matches the secure hash
    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {id}")
        raise InvalidHash

    file_size = file_id.file_size

    # Handle Range header for partial content requests
    if range_header:
        try:
            from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
            from_bytes = int(from_bytes)
            until_bytes = int(until_bytes) if until_bytes else file_size - 1
        except (ValueError, IndexError):
            logging.error("Invalid range header")
            return web.Response(
                status=416,
                body="416: Range not satisfiable",
                headers={"Content-Range": f"bytes */{file_size}"},
            )
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    # Validate the requested range
    if from_bytes >= file_size or until_bytes >= file_size or from_bytes < 0:
        logging.error("Invalid byte range")
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024  # Chunk size set to 1MB for smoother streaming
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil((until_bytes - offset + 1) / chunk_size)

    # Log range info for debugging
    logging.debug(
        f"Streaming file {id} from {from_bytes} to {until_bytes} (File size: {file_size})"
    )

    # Stream file chunks
    try:
        body = tg_connect.yield_file(
            file_id,
            index,
            offset,
            first_part_cut,
            last_part_cut,
            part_count,
            chunk_size,
        )
    except EOFError as eof_error:
        logging.error(f"EOFError while streaming file: {eof_error}")
        return web.Response(
            status=500, body="EOFError encountered while streaming the file."
        )
    except Exception as e:
        logging.error(f"Error during file streaming: {e}")
        return web.Response(status=500, body="Error during file streaming")

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    # Handle mime type and file name
    if mime_type:
        if not file_name:
            try:
                # Generate a default file name with the correct extension
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = (
                mimetypes.guess_type(file_id.file_name)[0] or "application/octet-stream"
            )
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    # Ensure file_name is properly formatted and sanitized
    file_name = file_name.replace('"', "").replace("/", "_")

    # Return the response with appropriate headers
    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
