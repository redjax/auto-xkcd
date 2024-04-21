from __future__ import annotations

from pathlib import Path
import typing as t

from core.paths import SERIALIZE_DIR
from loguru import logger as log
import msgpack

def serialize_dict(
    data: dict = None,
    output_dir: t.Union[str, Path] = None,
    filename: str = None,
    overwrite: bool = False,
) -> bool:
    """Serialize a `dict` to a file using `msgpack`.

    Params:
        data (dict): Input data to serialize
        output_dir (str|Path): Directory where `.msgpack` file will be saved.
        filename (str): The name of the `.msgpack` file. If `.msgpack` is omitted, it will be appended during validation.
        overwrite (bool): If `True`, serialization will occur even if the file already exists.

    """
    assert data, ValueError("Missing data dict to serialize.")
    assert isinstance(data, dict), TypeError(
        f"data must be a dict. Got type: ({type(data)})"
    )

    assert filename, ValueError("Missing an output filename")
    assert isinstance(filename, str), TypeError(
        f"filename should be a string. Got type: ({type(filename)})"
    )
    if not filename.endswith(".msgpack"):
        ## Append '.msgpack' if filename does not end with it already
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

            # raise exc

            return False

    ## Concatenate output_dir and filename into a Path object
    output_path: Path = Path(f"{output_dir}/{filename}")

    if not overwrite:
        ## Skip if file exists and overwrite=False
        if output_path.exists():
            log.warning(f"Serialized file already exists, skipping: {output_path}")
            return True

    ## Create msgpack
    try:
        packed = msgpack.packb(data)

    except Exception as exc:
        msg = Exception(f"Unhandled exception serializing input. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        # raise exc
        return False

    try:
        ## Save msgpack to file
        with open(file=output_path, mode="wb") as f:
            f.write(packed)

        return True
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving serialized data to file '{output_path}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        # raise exc

        return False
