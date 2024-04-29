from core import database, request_client
from core.dependencies import get_db
from core.config import db_settings
from core import paths
from packages import xkcd_comic
from domain.xkcd import comic


def count_total_comics() -> int:
    with get_db() as session:
        repo = comic.XKCDComicRepository(session)

        _count = repo.count()

    return _count
