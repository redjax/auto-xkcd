from pathlib import Path

from loguru import logger as log


def get_dir_size(scan_dir) -> tuple[int, str]:
    """Calculate the total size of a directory and return it as a tuple.

    Params:
        scan_dir (str or Path): The directory path to scan.

    Returns:
        (tuple): A tuple containing the total size in bytes (int) and a human-readable string.

    """
    try:
        total_size = 0

        for file_path in Path(scan_dir).rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        # Convert total size to human-readable format
        suffixes: list[str] = ["B", "KB", "MB", "GB", "TB"]
        i = 0

        total_size_bytes: int = total_size

        while total_size >= 1024 and i < len(suffixes) - 1:
            total_size /= 1024
            i += 1

        size_bytes: int = total_size_bytes
        size_str: str = f"{total_size:.2f}{suffixes[i]}"

        return size_bytes, size_str

    except Exception as e:
        return (None, str(e))
