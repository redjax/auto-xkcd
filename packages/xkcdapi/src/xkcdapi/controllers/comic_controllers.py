from __future__ import annotations

from contextlib import AbstractContextManager, contextmanager
import json
from pathlib import Path
import typing as t

from xkcdapi.helpers import (
    comic_num_req,
    current_comic_req,
    return_comic_num_url,
    return_current_comic_url,
)

import db_lib
from depends import db_depends
from domain import xkcd as xkcd_domain
from domain.xkcd.constants import (
    CURRENT_XKCD_URL,
    IGNORE_COMIC_NUMS,
    XKCD_URL_BASE,
    XKCD_URL_POSTFIX,
)
import http_lib
import httpx
from loguru import logger as log

class XkcdApiController(AbstractContextManager):
    def __init__(self, use_cache: bool = True, force_cache: bool = True, cache_ttl: int = 900, follow_redirects: bool = True):
        
        self.use_cache = use_cache
        self.force_cache = force_cache
        self.cache_ttl = cache_ttl
        self.follow_redirects = follow_redirects
        
        ## HTTP controller
        self.http_controller: http_lib.HttpxController | None = None
        
    def __enter__(self) -> t.Self:
        http_controller: http_lib.HttpxController = self._get_http_controller()
        self.http_controller = http_controller
        
        return self
    
    def __exit__(self, exc_type, exc_val, traceback) -> t.Literal[False] | None:
        if self.http_controller:
            if self.http_controller.client:
                self.http_controller.client.close()

        if exc_val:
            msg = f"({exc_type}) {exc_val}"
            log.error(msg)
            
            if traceback:
                log.error(f"Traceback: {traceback}")
            
            return False
        
        return
    
    def current_comic_url(self) -> str:
        return return_current_comic_url()
    
    def comic_url(self, comic_num: t.Union[int, str]) -> str:
        return return_comic_num_url(comic_num=comic_num)

    def _get_http_controller(self):
        http_controller: http_lib.HttpxController = http_lib.get_http_controller(use_cache=self.use_cache, force_cache=self.force_cache, follow_redirects=self.follow_redirects, cache_ttl=self.cache_ttl)
        
        return http_controller

    def get_current_comic(self) -> xkcd_domain.XkcdComicIn:
        req: httpx.Request = current_comic_req()
        
        with self.http_controller as http_ctl:
            res = http_ctl.send_request(req)

        if res.status_code != 200:
            log.warning(f"Non-200 response: [{res.status_code}: {res.reason_phrase}]")
            
            return
        
        ## Create dict from response
        res_dict: dict = http_lib.decode_response(response=res)
        ## Create XkcdApiResponseIn object
        comic_res: xkcd_domain.XkcdApiResponseIn = xkcd_domain.XkcdApiResponseIn(response_content=res_dict)
        ## Create XkcdComicIn object
        comic: xkcd_domain.XkcdComicIn = comic_res.return_comic_obj()
                
        return comic
        
    def get_comic(self, comic_num: t.Union[int, str]):
        req: httpx.Request = comic_num_req(comic_num=comic_num)
        
        with self.http_controller as http_ctl:
            res = http_ctl.send_request(request=req)
        
        if res.status_code != 200:
            log.warning(f"Non-200 response: [{res.status_code}: {res.reason_phrase}]")
            
        ## Create dict from response
        res_dict: dict = http_lib.decode_response(response=res)
        ## Create XkcdApiResponseIn object
        comic_res: xkcd_domain.XkcdApiResponseIn = xkcd_domain.XkcdApiResponseIn(response_content=res_dict)
        ## Create XkcdComiIn object
        comic: xkcd_domain.XkcdComicIn = comic_res.return_comic_obj()
        
        return comic

    def get_comic_img(self, comic: t.Union[xkcd_domain.XkcdComicIn, xkcd_domain.XkcdComicOut]):
        req: httpx.Request = http_lib.build_request(url=comic.img_url)
        
        with self.http_controller as http_ctl:
            res: httpx.Response = http_ctl.send_request(request=req)
        
            if res.status_code != 200:
                log.warning(f"Non-200 response: [{res.status_code}: {res.reason_phrase}]")
                
                return

            img_bytes: bytes = res.content
            
            comic_img: xkcd_domain.XkcdComicImgIn = xkcd_domain.XkcdComicImgIn(num=comic.num, img_bytes=img_bytes)
            
            return comic_img
    
    def get_comic_and_img(self, comic_num: t.Union[int, str]) -> t.Tuple[xkcd_domain.XkcdComicIn, xkcd_domain.XkcdComicImgIn]:
        log.debug(f"Request comic #{comic_num}")
        try:
            comic: xkcd_domain.XkcdComicImgIn = self.get_comic(comic_num=comic_num)
        except Exception as exc:
            msg = f'({type(exc)}) Error requesting comic #{comic_num}. Details: {exc}'
            log.error(msg)
            
            raise exc
        
        if not comic:
            raise ValueError(f"Error getting comic #{comic_num}")
        
        log.debug(f"Request image for comic #{comic_num}")
        try:
            comic_img: xkcd_domain.XkcdComicImgIn = self.get_comic_img(comic=comic)
        except Exception as exc:
            msg = f"({type(exc)}) Error requesting image for comic #{comic_num}. Details: {exc}"
            log.error(msg)
            
            raise exc
        
        if not comic_img:
            raise ValueError(f"Error getting image for comic #{comic.num}")
        
        return comic, comic_img
