from __future__ import annotations

import json
from pathlib import Path
import typing as t

from modules.requests_prefab import telegram_chatid_req

from core import paths, request_client
import httpx
from loguru import logger as log
import telegram

def save_chatid_to_file(
    chat_id: t.Union[str, int] = None,
    file: t.Union[str, Path] = paths.TELEGRAM_CHAT_ID_FILE,
    overwrite: bool = False,
) -> None:
    file: Path = Path(f"{file}")
    chat_id: str = str(chat_id)

    if file.exists():
        if not overwrite:
            log.warning(
                f"Chat ID file already exists at '{chat_id}'. To overwrite, call save_chatid_to_file(overwrite=True)"
            )
            return

    try:
        with open(file, "w") as f:
            f.write(chat_id)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception writing chat ID to file '{file}'. Details: {exc}"
        )
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
        # log.info(f"Response content:\n{_content}")
        if not _content["result"]:
            log.warning(
                f"Chats list empty. Please send a chat to the bot before retrying."
            )
            return
        try:
            chat_id: int = _content["result"][0]["message"]["chat"]["id"]
            # log.success(f"Extracted chat ID [{chat_id}].")

            return chat_id
        except Exception as exc:
            msg = Exception(f"Unhandled exception extracting chat ID. Details: {exc}")
            log.error(msg)

            raise msg


def request_chat_id(bot_token: str = None) -> httpx.Response:
    req: httpx.Request = telegram_chatid_req(bot_token=bot_token)

    ## Make request to getUpdates
    try:
        with httpx.Client() as client:
            res: httpx.Response = client.send(request=req)
            if not res.status_code == 200:
                log.warning(f"[{res.status_code}: {res.reason_phrase}]: {res.text}")

            return res

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception requesting Telegram bot's getUpdates. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def get_chat_token(
    bot_token: str = None,
    save_to_file: bool = False,
    output_file: t.Union[str, Path] = None,
    overwrite: bool = False,
) -> str:
    log.info(f"Making request to bot's /getUpdates endpoint")
    try:
        chat_id_res: httpx.Response = request_chat_id(bot_token=bot_token)
    except Exception as exc:
        msg = Exception(f"Unhandled exception requesting chat ID. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    log.info("Extracting chat ID from Response")
    ## Extract the chat ID from the Response
    try:
        chat_id: str | None = extract_chatid_from_response(response=chat_id_res)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception extracting chat ID from Response. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    if chat_id_res.status_code == 200:
        if chat_id is None:
            ## Response success, but chat ID not found.
            log.warning(
                "getUpdates request successful, but not chat ID found. Send a message to the bot/chat before retrying."
            )

            raise ValueError(
                "No chat ID found. Send a message to the bot/chat before retrying."
            )

        else:
            log.success("Chat ID extracted")

            if save_to_file:
                if not output_file:
                    msg = ValueError(
                        f"save_to_file is True, but not output_file specified."
                    )
                    log.error(msg)

                    raise msg

                log.info(f"Saving chat ID to file '{output_file}'")
                try:
                    save_chatid_to_file(
                        chat_id=chat_id, file=output_file, overwrite=overwrite
                    )
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception saving chat ID to file '{output_file}'. Details: {exc}"
                    )
                    log.error(msg)
                    log.trace(exc)

                    raise exc

            return chat_id

    else:
        ## Non-200 response
        msg = ValueError(
            f"Non-200 response code requesting Telegram chat ID: [{chat_id_res.status_code}: {chat_id_res.reason_phrase}]: {chat_id_res.text}"
        )
        raise msg
