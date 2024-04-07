from __future__ import annotations

from pathlib import Path
import typing as t

from loguru import logger as log

def save_bytes(
    img_bytes: bytes = None,
    output_dir: t.Union[str, Path] = None,
    output_filename: str = None,
):
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

    output_path: Path = Path(f"{output_dir}/{output_filename}")
    if not output_path.parent.exists():
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

    # log.debug(f"Saving image bytes.")
    try:
        with open(output_path, "wb") as f:
            f.write(img_bytes)
            log.success(f"Image saved to path '{output_path}'")

        return True
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving image to path '{output_path}'. Details: {exc}"
        )
        log.error(msg)

        # raise msg

        return False
