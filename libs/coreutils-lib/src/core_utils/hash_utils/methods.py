from __future__ import annotations

import hashlib

from loguru import logger as log

def get_hash_from_str(input_str: str = None, encoding: str = "utf-8") -> str:
    """Return a hashed version of an input string.

    Params:
        input_str (str): The string to hash
        encoding (str): The character encoding to use

    Returns:
        (str): A hashed representation of `input_str`

    Raises:
        ValueError: When input validation fails
        Exception: A generic `Exception` when converting string to hash fails

    """
    if not input_str:
        raise ValueError("Missing input string")

    if not encoding:
        raise ValueError("Missing encoding")

    if not isinstance(input_str, str):
        try:
            input_str: str = str(input_str)

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception converting input string ({type(input_str)}) to str()"
            )
            log.error(msg)

            raise exc

    try:
        hash = hashlib.md5(input_str.encode(encoding)).hexdigest()

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting string to hash. Details: {exc}"
        )
        log.error(msg)

        raise exc

    return hash


if __name__ == "__main__":
    log.info(f"Hashlib demo start")

    _str: str = (
        "This is a test string to be hashed. It has alphanumeric characters like 'a' and 3, and special characters!"
    )

    hashed = get_hash_from_str(input_str=_str)
    print(f"Hashed ({type(hashed)}): {hashed}")
