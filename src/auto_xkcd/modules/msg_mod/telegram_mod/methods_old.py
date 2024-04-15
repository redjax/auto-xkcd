from __future__ import annotations

import json
from pathlib import Path
import typing as t

from core.config import TelegramSettings
from core import request_client
import hishel
import httpx
from loguru import logger as log
import msgpack
import telegram


def get_telegram_bot(bot_token: str = None) -> telegram.Bot:
    """Return an initialized Telegram bot."""
    assert bot_token is not None, ValueError("bot_token cannot be None")

    bot: telegram.Bot = telegram.Bot(token=bot_token)

    return bot


def telegram_bot_updates_url(bot_token: str = None) -> str:
    """Return a formatted URL string for a Telegram bot's /getUpdates route."""
    assert bot_token is not None, ValueError("Must pass a bot_token")
    assert isinstance(bot_token, str), TypeError(
        f"bot_token must be of type str. Got type: ({type(bot_token)})"
    )

    TELEGRAM_BOT_INFO_URL: str = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    return TELEGRAM_BOT_INFO_URL


def request_bot_getupdates(
    telegram_bot_getupdates_url: str = None,
    cache_transport: hishel.CacheTransport = None,
) -> httpx.Response:
    request: httpx.Request = httpx.Request("GET", telegram_bot_getupdates_url)

    try:
        with request_client.HTTPXController(transport=cache_transport) as httpx_ctl:
            res: httpx.Response = httpx_ctl.send_request(request=request)

            if res.status_code in [200]:
                log.success(f"Telegram bot chat retrieved.")
                log.info(
                    f"Telegram getUpdates response: [{res.status_code}: {res.reason_phrase}]"
                )

                return res

    except Exception as exc:
        msg = Exception(f"Unhandled exception getting bot updates. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc


def extract_chatid_from_response(response: httpx.Response = None) -> str | None:
    _content: dict = json.loads(response.content.decode("utf-8"))
    if not _content:
        log.warning(
            f"Conversation is empty. Please send at least 1 message to the bot."
        )
        return None
    else:
        log.info(f"Response content:\n{_content}")
        if not _content["result"]:
            log.warning(
                f"Chats list empty. Please send a chat to the bot before retrying."
            )
            return
        try:
            chat_id: int = _content["result"][0]["message"]["chat"]["id"]
            log.success(f"Extracted chat ID [{chat_id}].")

            return chat_id
        except Exception as exc:
            msg = Exception(f"Unhandled exception extracting chat ID. Details: {exc}")
            log.error(msg)

            raise msg


def get_chat_id(
    telegram_settings: TelegramSettings = None,
    cache_transport: hishel.CacheTransport = None,
    serial_file: t.Union[str, Path] = None,
) -> str:
    """Request a Telegram bot's chat ID."""
    assert telegram_settings is not None, ValueError("telegram_settings cannot be None")
    assert isinstance(telegram_settings, TelegramSettings), TypeError(
        f"telegram_settings should be of type TelegramSettings. Got type: ({type(telegram_settings)})"
    )
    assert telegram_settings.bot_token is not None, ValueError(
        "TelegramSettings.bot_token cannot be None"
    )

    assert cache_transport is not None, ValueError("cache_transport cannot be None")

    assert serial_file is not None, ValueError("serial_file cannot be None")
    assert isinstance(serial_file, str) or isinstance(serial_file, Path), TypeError(
        f"serial_file should be of type str or Path. Got type: ({type(serial_file)})"
    )
    if isinstance(serial_file, str):
        serial_file: Path = Path(serial_file)

    if not serial_file.exists():
        if not serial_file.parent.exists():
            serial_file.parent.mkdir(parents=True, exist_ok=True)

        log.warning(
            f"Did not find Telegram chat ID serialized at path '{serial_file}'. Requesting chat ID."
        )
        try:
            TELEGRAM_BOT_INFO_URL: str = telegram_bot_updates_url(
                bot_token=telegram_settings.bot_token
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception building Telegram bot <@{telegram_settings.bot_username}> /getUpdates URL. Details: {exc}"
            )
            log.error(msg)

            raise msg

        chat_getupdates_res: httpx.Response = request_bot_getupdates(
            telegram_bot_getupdates_url=TELEGRAM_BOT_INFO_URL,
            cache_transport=cache_transport,
        )

        chat_id: str | None = extract_chatid_from_response(response=chat_getupdates_res)

        if not chat_id:
            raise ValueError(
                "chat_id should not have been empty. Send a message to the bot, then try again."
            )

        log.info(f"Saving chat ID to file '{serial_file}'")
        try:
            packed = msgpack.packb(chat_id)

            try:
                with open(serial_file, "wb") as f:
                    f.write(packed)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception saving chat_id to file '{serial_file}'. Details: {exc}"
                )
                log.error(msg)

        except Exception as exc:
            msg = Exception(f"Unhandled exception creating msgpack. Details: {exc}")
            log.error(msg)

        return chat_id
    else:
        chat_id = load_serialized_chat_id(file=serial_file)

        return chat_id


def send_photo_msg(
    bot: telegram.Bot = None,
    chat_id: int = None,
    photo: bytes = None,
    caption: str | None = None,
):
    """Send a Telegram message to chat by ID, include a photo and optional caption."""
    try:
        bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)
        log.success(f"Sent photo chat ID: {chat_id}")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception sending Telegram photo message. Details: {exc}"
        )
        log.error(msg)

        raise msg


def load_serialized_chat_id(file: t.Union[str, Path] = None) -> str | None:
    """Load a Telegram chat ID from a serialized file, if it exists."""
    assert file is not None, ValueError("file cannot be None")
    assert isinstance(file, str) or isinstance(file, Path), TypeError(
        f"file must be of type str or Path. Got type: ({type(file)})"
    )
    if isinstance(file, Path):
        file: str = f"{file}"

    if not Path(file).exists():
        log.warning(f"Could not find serialized chat ID file '{file}'")
        return None

    log.info(f"Loading Telegram chat ID from file '{file}'")
    try:
        with open(file, "rb") as f:
            data_bytes: bytes = f.read()
            chat_id: str = msgpack.unpackb(data_bytes)

        return chat_id
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading Telegram chat ID from file '{file}'. Details: {exc}"
        )
        log.warning(msg)

        return None


def save_serialized_chat_id(chat_id: str = None, file: str = None) -> None:
    """Save a Telegram chat ID to a file."""
    assert file is not None, ValueError("file cannot be None")
    assert isinstance(file, str) or isinstance(file, Path), TypeError(
        f"file must be of type str or Path. Got type: ({type(file)})"
    )
    if isinstance(file, Path):
        file: str = f"{file}"

    packed = msgpack.packb(chat_id)

    try:
        with open(file, "wb") as f:
            f.write(packed)
        log.success(f"Serialized chat_id to file '{file}'.")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception serializing chat ID to file '{file}'. Detaails: {exc}"
        )
        log.error(msg)

        raise msg
