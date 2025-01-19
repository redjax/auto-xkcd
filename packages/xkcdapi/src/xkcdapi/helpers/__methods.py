from loguru import logger as log
import typing as t

import http_lib
from xkcdapi.constants import XKCD_URL_BASE, XKCD_URL_POSTFIX, CURRENT_XKCD_URL

import httpx

def return_comic_num_url(comic_num: t.Union[int, str] = None) -> str:
    if not comic_num:
        raise ValueError("Missing a comic number")
    if not isinstance(comic_num, int) or not isinstance(comic_num, str):
        raise TypeError(f"Invalid type for comic_num: ({type(comic_num)}). Must be an int or str.")

    ## Build URL from input comic_num
    _url: str = f"{XKCD_URL_BASE}/{comic_num}/{XKCD_URL_POSTFIX}"
    
    return _url
    

def return_current_comic_url() -> str:
    return CURRENT_XKCD_URL
    

def comic_num_req(comic_num: t.Union[int, str] = None) -> httpx.Request:
    """Build an `httpx.Request` object from an input comic number.

    Params:
        comic_num (int, str): A comic number to request, i.e. 42.

    Returns:
        (httpx.request): An initialized `httpx.Request` for the given `comic_num`.

    """
    _url: str = return_comic_num_url(comic_num=comic_num)

    # log.debug(f"Requesting URL for comic #{comic_num}: {_url}")
    try:
        ## Build the request
        req: httpx.Request = http_lib.build_request(url=_url)

        return req

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building request for comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)

        raise msg
    
    
def current_comic_req() -> httpx.Request:
    _url: str = return_comic_num_url()
    
    try:
        ## Build the request
        req: httpx.Request = http_lib.build_request(url=_url)
    
        return req
    except Exception as exc:
        msg = f"({type(exc)}) Error building current comic Request object. Details: {exc}"
        log.error(msg)
        
        raise exc
