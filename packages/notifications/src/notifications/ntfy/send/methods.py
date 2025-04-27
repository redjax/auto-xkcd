from __future__ import annotations

from datetime import datetime
import json
import logging
from pathlib import Path
import typing as t

log = logging.getLogger(__name__)

from domain.ntfy import BroadcastAction, HttpAction, ViewAction
import http_lib
import httpx

__all__ = ["send_message", "send_file"]


def send_message(
    topic_url: str,
    messsage: str,
    headers: dict,
    title: str | None = None,
    priority: str = "default",
    tags: list[str] = [],
    actions: list[t.Union[ViewAction, BroadcastAction, HttpAction]] = [],
    schedule: datetime | None = None,
    format_as_markdown: bool = False,
    timeout: int = 5,
):
    msg_headers = {
        "X-Title": title,
        "X-Priority": priority,
        "X-Tags": ",".join(tags),
        "Markdown": str(format_as_markdown).lower(),
    }

    headers = headers | msg_headers

    if len(actions) > 0:
        headers["X-Actions"] = " ; ".join(action.headers for action in actions)

    if schedule:
        headers["X-Delay"] = str(int(schedule.timestamp()))

    log.debug(f"Headers: {headers}")

    req = http_lib.build_request("POST", url=topic_url, data=messsage, headers=headers)

    http_controller = http_lib.get_http_controller(use_cache=False, timeout=timeout)

    with http_controller as http_ctl:
        res = http_ctl.send_request(req)

    return res


def send_file(
    topic_url: str,
    headers: dict,
    file: t.Union[str, Path, bytes],
    title: str | None = None,
    priority: str = "default",
    tags: list[str] = [],
    actions: list[t.Union[BroadcastAction, HttpAction, ViewAction]] = [],
    schedule: datetime | None = None,
    timeout: int = 30,
):
    if isinstance(file, str) or isinstance(file, Path):
        file: Path = (
            Path(str(file)).expanduser() if "~" in str(file) else Path(str(file))
        )

        if not file.exists():
            raise FileNotFoundError(f"File '{file.name}' not found at path '{file}'.")

        try:
            with open(str(file), "rb") as f:
                file_contents = f.read()
        except Exception as exc:
            log.error(f"({type(exc)}) Error reading from file '{file}'. Details: {exc}")
            raise

    elif isinstance(file, bytes):
        file_contents = file

    file_headers = {
        "X-Title": str(title),
        "X-Filename": str(file).split("/")[-1],
        "X-Priority": priority,
        "X-Tags": ",".join(tags),
        "X-Actions": " ; ".join([action.headers for action in actions]),
    }
    headers = headers | file_headers

    if schedule:
        headers = headers | {"X-Delay": str(int(schedule.timestamp()))}

    req: httpx.Request = http_lib.build_request(
        "POST", url=topic_url, headers=headers, data=file_contents
    )

    http_controller = http_lib.get_http_controller(use_cache=False, timeout=timeout)

    log.info(f"Posting file to '{topic_url}'")
    try:
        with http_controller as http_ctl:
            res = http_ctl.send_request(request=req)
            res.raise_for_status()
    except Exception as exc:
        log.error(f"Error sending file bytes to topic '{topic_url}'. Details: {exc}")
        raise

    log.debug(f"[{res.status_code}:{res.reason_phrase}]")
