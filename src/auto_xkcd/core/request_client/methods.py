"""Methods to handle generic HTTPX data."""

from __future__ import annotations

import json
from pathlib import Path
import typing as t

import httpx
from loguru import logger as log


def save_bytes(
    _bytes: bytes = None,
    output_dir: t.Union[str, Path] = None,
    output_filename: str = None,
) -> bool:
    """Save bytestring to a file.

    Params:
        _bytes (bytes): A bytestring to save to a file.
        output_dir (str|Path): Directory where bytes file will be saved.
        output_filename (str): Name of the file to be saved at `output_dir/`output_filename`.

    """
    assert output_dir, ValueError("Missing output directory path")
    assert isinstance(output_dir, str) or isinstance(output_dir, Path), TypeError(
        f"output_dir must be a str or Path. Got type: ({type(output_dir)})"
    )
    if isinstance(output_dir, Path):
        if "~" in f"{output_dir}":
            _dir: Path = output_dir.expanduser()
            output_dir = _dir
    elif isinstance(output_dir, str):
        if "~" in output_dir:
            output_dir: Path = Path(output_dir).expanduser()
        else:
            output_dir: Path = Path(output_dir)

    assert output_filename, ValueError("Missing output filename")
    assert isinstance(output_filename, str), TypeError(
        f"output_filename must be a string. Got type: ({type(output_filename)})"
    )

    assert _bytes, ValueError("Missing bytestring to save.")
    assert isinstance(_bytes, bytes), TypeError(
        f"_bytes must be of type bytes. Got type: ({type(_bytes)})"
    )

    ## Concatenate output_dir and output_filename into a Path object
    output_path: Path = Path(f"{output_dir}/{output_filename}")
    if not output_path.parent.exists():
        ## Create output_dir if it does not exist.
        log.warning(
            f"Parent directory '{output_path.parent}' does not exist. Creating."
        )
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory '{output_path.parent}'. Details: {exc}"
            )
            log.error(msg)

            raise msg

    ## Save img bytes
    try:
        with open(output_path, "wb") as f:
            f.write(_bytes)
            log.success(f"Image saved to path '{output_path}'")

        return True

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving image to path '{output_path}'. Details: {exc}"
        )
        log.error(msg)

        # raise msg

        return False


def build_request(
    method: str = "GET",
    url: str = None,
    headers: dict | None = {"Content-Type": "application/json"},
    params: dict | None = None,
    data: t.Union[dict, str] | None = None,
) -> httpx.Request:
    """Assemble an httpx.Request instance from inputs.

    Params:
        method (str): The request method type, i.e. "GET", "POST", "PUT", "DELETE".
        url (str): The URL to request.
        headers (dict|None): Optional request headers dict.
        params (dict|None): Optional request params dict.
        data (dict|str|None): Optional request data.

    Returns:
        (httpx.Request): An initialized `httpx.Request` object.

    """
    assert method, ValueError("Missing a request method")
    assert isinstance(method, str), TypeError(
        f"method must be of type str. Got type: ({type(method)})"
    )
    method = method.upper()

    assert url, ValueError("Missing a request URL")
    assert isinstance(url, str), TypeError(
        f"url must be a string. Got type: ({type(url)})"
    )

    if headers:
        assert isinstance(headers, dict), TypeError(
            f"headers should be a dict. Got type: ({type(headers)})"
        )
    if params:
        assert isinstance(params, dict), TypeError(
            f"params should be a dict. Got type: ({type(params)})"
        )
    if data:
        assert isinstance(data, dict) or isinstance(data, str), TypeError(
            f"data should be a Python dict or JSON string. Got type: ({type(data)})"
        )

        if isinstance(data, dict):
            _data: str = json.dumps(data)
            data = _data

    try:
        req: httpx.Request = httpx.Request(
            method=method, url=url, headers=headers, params=params, data=data
        )

        return req

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building {method} request to URL: {url}. Details: {exc}"
        )
        log.error(msg)

        raise msg
