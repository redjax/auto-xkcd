from __future__ import annotations

import typing as t

from core import get_db, request_client
from fastapi import Depends
import hishel
import sqlalchemy.orm as so

cache_transport_dependency = t.Annotated[
    hishel.CacheTransport, Depends(request_client.get_cache_transport)
]

db_dependency = t.Annotated[t.Generator[so.Session, t.Any, None], Depends(get_db)]
