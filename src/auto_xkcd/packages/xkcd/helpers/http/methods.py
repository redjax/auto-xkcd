from core import request_client
from utils import serialize_utils

import httpx
from loguru import logger as log
from red_utils.std import hash_utils


def parse_comic_response(res: httpx.Response = None) -> dict:
    try:
        content: dict = request_client.decode_res_content(res=res)

        return content

    except Exception as exc:
        msg = Exception(f"Unhandled exception parsing comic response. Details: {exc}")
        log.error(msg)

        raise msg


def serialize_response(res: httpx.Response = None, filename: str = None):
    assert filename, ValueError("Mising a filename")

    content: dict = request_client.decode_res_content(res=res)

    filename_hash: str = hash_utils.get_hash_from_str(filename)

    try:
        serialize_utils.serialize_dict(data=content, filename=filename)

        return True
    except Exception as exc:
        msg = Exception(f"Unhandled exception serializing data. Details: {exc}")
        log.error(msg)

        return False
