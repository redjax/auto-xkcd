from __future__ import annotations

import typing as t

from fastapi.responses import Response

API_RESPONSES_DICT: dict[int, dict[str, t.Any]] = {404: {"description": "Not found"}}


def img_response(img_bytes: bytes = None, media_type: str = "image/png") -> Response:
    assert img_bytes, ValueError("Missing image bytestring")
    assert isinstance(img_bytes, bytes), TypeError(
        f"img_bytes must be a bytestring. Got type: ({type(img_bytes)})"
    )

    res: Response = Response(
        content=img_bytes,
        media_type=media_type,
    )

    return res
