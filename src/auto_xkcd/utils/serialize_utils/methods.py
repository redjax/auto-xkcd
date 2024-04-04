from __future__ import annotations

from pathlib import Path
import typing as t

from core.paths import SERIALIZE_DIR
from loguru import logger as log
import msgpack


def serialize_dict(
    data: dict = None, output_dir: t.Union[str, Path] = None, filename: str = None
):
    assert data, ValueError("Missing data dict to serialize.")
    assert isinstance(data, dict), TypeError(
        f"data must be a dict. Got type: ({type(data)})"
    )

    assert filename, ValueError("Missing an output filename")
    assert isinstance(filename, str), TypeError(
        f"filename should be a string. Got type: ({type(filename)})"
    )
    if not filename.endswith(".msgpack"):
        filename: str = f"{filename}.msgpack"

    if output_dir is None:
        output_dir: Path = Path(f"{SERIALIZE_DIR}/comic_responses")
    else:
        assert isinstance(output_dir, str) or isinstance(output_dir, Path), TypeError(
            f"output_dir must be a string or Path object. Got type: ({type(output_dir)})"
        )
        if isinstance(output_dir, str):
            output_dir: Path = Path(output_dir)
        if "~" in f"{output_dir}":
            output_dir: Path = output_dir.expanduser()

    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory '{output_dir}'. Details: {exc}"
            )
            log.trace(exc)

            raise exc

    output_path: Path = Path(f"{output_dir}/{filename}")

    try:
        packed = msgpack.packb(data)
        log.debug(f"Serialized object type: {type(packed)}")
    except Exception as exc:
        msg = Exception(f"Unhandled exception serializing input. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    if output_path.exists():
        log.debug(f"Output path exists, skipping: {output_path}")
        return

    try:
        with open(output_path, "wb") as f:
            f.write(packed)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving serialized data to file '{output_path}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc
