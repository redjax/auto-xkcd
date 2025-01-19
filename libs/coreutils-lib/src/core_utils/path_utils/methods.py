from __future__ import annotations

import re

def sanitize_filename(filename: str, space_replacement: str = "_", unsafe_char_replacement: str = "-") -> str:
    """Sanitizes a filename to be safe for all OS paths by replacing unsafe characters.
    
    Params:
        filename (str): The original filename.
        space_replacement (str): Replacement for spaces. Default is "_".
        unsafe_char_replacement (str): Replacement for other unsafe characters. Default is "-".
        
    Returns:
        str: The sanitized filename.

    """
    # Characters that are generally unsafe for filenames
    unsafe_characters = r'[<>:"/\\|?*]'
    
    # Replace spaces with the defined space replacement
    filename = filename.replace(" ", space_replacement)
    
    # Replace other unsafe characters with the defined unsafe character replacement
    filename = re.sub(unsafe_characters, unsafe_char_replacement, filename)
    
    # Strip leading and trailing whitespace or replacement characters
    filename = filename.strip(unsafe_char_replacement + space_replacement)
    
    return filename
