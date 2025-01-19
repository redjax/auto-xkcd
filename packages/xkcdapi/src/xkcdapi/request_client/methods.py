from loguru import logger as log

import typing as t

import core_utils
import http_lib

from xkcdapi.helpers import comic_num_req, current_comic_req, return_comic_num_url, return_current_comic_url

import httpx


def request_current_xkcd_comic(use_cache: bool = True, force_cache: bool = True, follow_redirects: bool = True) -> httpx.Response:
    req: httpx.Request = current_comic_req()
    
    http_controller: http_lib.HttpxController = http_lib.get_http_controller(use_cache=use_cache, force_cache=force_cache, follow_redirects=follow_redirects)
    
    with http_controller as http_ctl:
        try:
            res = http_ctl.send_request(req)
            log.debug(f"Current XKCD comic response: [{res.status_code}: {res.reason_phrase}]")
            
            return res
        except Exception as exc:
            msg = f"({type(exc)}) Error requesting current XKCD comic. Details: {exc}"
            log.error(msg)
            
            raise exc
