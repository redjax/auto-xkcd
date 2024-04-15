"""Click modules for interacting with the app's pipelines.

See all commands with `$ cli.py pipelines --help`
"""

from __future__ import annotations

from ._cli import pipelines_cli
from .commands import get_current_comic, list_pipelines
