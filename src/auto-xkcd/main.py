from core.request_client import HTTPXController

import httpx
import hishel


from loguru import logger as log

XKCD_BASE_URL: str = "https://xkcd.com"
CURRENT_COMIC_ENDPOINT: str = "/info.0.json"
CURRENT_COMIC_URL: str = f"{XKCD_BASE_URL}/{CURRENT_COMIC_ENDPOINT}"

if __name__ == "__main__":
    req: httpx.Request = httpx.Request(method="GET", url=CURRENT_COMIC_URL)

    with HTTPXController() as httpx_ctl:
        res: httpx.Response = httpx_ctl.send_request(request=req)
        log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")
