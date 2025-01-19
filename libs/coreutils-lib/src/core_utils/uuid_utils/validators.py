from __future__ import annotations

import logging

log = logging.getLogger(__name__)

from .constants import UUIDLength

## Instantiated UUIDLength class
glob_uuid_lens: UUIDLength = UUIDLength()


def validate_trim(trim_in: int = 0, as_hex: bool = False) -> int:
    """Validate a trim value.

    Params:
        trim_in (int): Value of `trim` passed from another function.
        as_hex (bool): Value of `as_hex` passed from another function.

    Returns:
        (int): A validated `int`

    Raises:
        ValueError: When `trim_in` is less than 0, or greater than the length of a UUID string/hex (36/32 characters).

    """
    if not isinstance(trim_in, int):
        ## If trim_in is not an int, try converting to one
        try:
            trim_in = int(trim_in)
        except Exception as exc:
            raise Exception(
                f"Unhandled exception converting trim value to int. Errored on converting input (type: {type(trim_in)}): {trim_in}. Details: {exc}"
            )

    if as_hex:
        ## Set length of UUID hex string (without '-' characters)
        uuid_len: int = glob_uuid_lens.hex
    else:
        ## Set length of UUID to standard 36 characters
        uuid_len: int = glob_uuid_lens.standard

    if not trim_in >= 0:
        raise ValueError(f"Trim value must be 0 or greater.")

    ## Check that trim_in does not exceed length of UUID string
    if trim_in >= uuid_len:
        exc_msg: str = (
            f"Trim value must be less than {uuid_len}. At least 1 character must be returned."
        )

        if as_hex:
            exc_msg: str = (
                f"{exc_msg} Note that a hexadecimal UUID string is only 32 characters because of the missing '-' characters."
            )

        raise ValueError(exc_msg)

    return trim_in


def validate_characters(characters_in: int = 0, as_hex: bool = False) -> int:
    """Validate a characters value.

    Params:
        characters_in (int): Integer value passed from another function
        as_hex (int): Bool value passed from another function

    Raises:
        Exception: When attempting to convert `characters_in` value to an `int` fails.
        ValueError: When `trim_in` is less than 0, or greater than the length of a UUID string/hex (36/32 characters).

    """
    if not isinstance(characters_in, str):
        try:
            characters_in = int(characters_in)
        except Exception as exc:
            raise Exception(
                f"Unhandled exception converting characters value to int. Errored on converting int (type: {type(characters_in)}): {characters_in}. Details: {exc}"
            )

    if as_hex:
        ## Set length of UUID hex string (without '-' characters)
        uuid_len: int = glob_uuid_lens.hex

        ## If characters_in is greater than uuid_len, set trim to max number of characters
        if characters_in > uuid_len:
            characters_in = uuid_len

    else:
        uuid_len: int = glob_uuid_lens.standard

        if characters_in > uuid_len:
            raise ValueError(
                f"Character count must be less than UUID string length ({uuid_len})"
            )

    if not characters_in >= 0:
        raise ValueError(f"Trim value must be 0 or greater.")

    if characters_in >= uuid_len:
        exc_msg: str = (
            f"Trim value must be less than {uuid_len}. At least 1 character must be returned."
        )

        if as_hex:
            exc_msg: str = (
                f"{exc_msg} Note that a hexadecimal UUID string is only {glob_uuid_lens.hex} characters because of the missing '-' characters."
            )

        raise ValueError(exc_msg)

    return characters_in
