from __future__ import annotations

from core.paths import CACHE_DIR
import hishel
import httpx

CACHE_STORAGE: hishel.FileStorage = hishel.FileStorage(base_path=f"{CACHE_DIR}/hishel")
CACHE_TRANSPORT = hishel.CacheTransport(
    transport=httpx.HTTPTransport(), storage=CACHE_STORAGE
)
