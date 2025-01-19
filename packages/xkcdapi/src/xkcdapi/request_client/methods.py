from loguru import logger as log

import typing as t
import json

import core_utils
import http_lib

from xkcdapi.helpers import comic_num_req, current_comic_req, return_comic_num_url, return_current_comic_url

import httpx


def request_current_xkcd_comic(use_cache: bool = False, force_cache: bool = False, follow_redirects: bool = False) -> httpx.Response:
    req: httpx.Request = current_comic_req()
    
    http_controller: http_lib.HttpxController = http_lib.get_http_controller(use_cache=use_cache, force_cache=force_cache, follow_redirects=follow_redirects)
    
    try:    
        with http_controller as http_ctl:
            res = http_ctl.send_request(req)
            log.debug(f"Current XKCD comic response: [{res.status_code}: {res.reason_phrase}]")
            
            return res
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting current XKCD comic. Details: {exc}"
        log.error(msg)
        
        raise exc


def request_xkcd_comic_img(img_url: str, use_cache: bool = False, force_cache: bool = False, follow_redirects: bool = False) -> httpx.Response:
    req: httpx.Request = http_lib.build_request(url=img_url)
    
    http_controller: http_lib.HttpxController = http_lib.get_http_controller(use_cache=use_cache, force_cache=force_cache,  follow_redirects=follow_redirects)
    
    try:
        with http_controller as http_ctl:
            res =  http_ctl.send_request(req)
            log.debug(f"XKCD comic image response: [{res.status_code}: {res.reason_phrase}]")
            
            return res
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting comic image. Details: {exc}"
        log.error(msg)
        
        raise exc
