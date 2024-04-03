from __future__ import annotations

import time

from loguru import logger as log

def pause(duration: int = 5, pause_msg: str | None = "Sleeping 5 seconds...") -> None:
    assert duration, ValueError("Missing a pause duration")
    assert isinstance(duration, int) and duration > 0, TypeError(
        f"duration must be a non-zero positive integer. Got type: ({type(duration)})"
    )

    if pause_msg:
        assert isinstance(pause_msg, str), TypeError(
            f"pause_msg must be a string. Got type: ({type(pause_msg)})"
        )

    log.info(pause_msg)

    time.sleep(duration)

    return
