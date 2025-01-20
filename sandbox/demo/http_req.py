from __future__ import annotations

import db_lib
from depends import db_depends
import http_lib
from loguru import logger as log
import settings
import setup

if __name__ == "__main__":
    setup.setup_loguru_logging(
        log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"),
        colorize=True,
    )

    log.info("[DEMO] HTTP request with http_lib")

    req = http_lib.build_request(url="https://www.google.com")

    with http_lib.get_http_controller() as http_ctl:
        res = http_ctl.send_request(request=req)
        log.info(f"Demo request response: [{res.status_code}: {res.reason_phrase}]")
