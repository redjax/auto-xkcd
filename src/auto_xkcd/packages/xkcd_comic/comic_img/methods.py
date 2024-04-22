import typing as t
from pathlib import Path

from core import paths
from core.dependencies import get_db
from domain.xkcd import comic
from helpers import validators

from loguru import logger as log


def lookup_img_file(
    search_dir: t.Union[str, Path] = paths.COMIC_IMG_DIR, comic_num: int = None
) -> Path | None:
    search_dir = validators.validate_path(p=search_dir)

    log.debug(f"Searching '{search_dir}' for XKCD comic #{comic_num} image file...")
    try:
        for img_f in search_dir.glob("**/*.png"):
            if img_f.stem == f"{comic_num}":
                log.debug(f"Found XKCD comic #{comic_num} image file: {img_f}")

                return img_f

        log.warning(
            f"Did not find image file for XKCD comic #{comic_num} in path '{search_dir}'."
        )

        return None
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception retrieving comic #{comic_num} image file. Details: {exc}"
        )
        log.error(msg)
        log.trace(msg)

        raise msg


def retrieve_img_from_db(comic_num: int = None) -> comic.XKCDComicImage | None:
    try:
        with get_db() as session:
            repo: comic.XKCDComicImageRepository = comic.XKCDComicImageRepository(
                session=session
            )

            try:
                db_comic_img: comic.XKCDComicImageModel = repo.get_by_comic_num(
                    comic_num=comic_num
                )
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception getting comic image for XKCD comic #{comic_num}. Details: {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc

            if db_comic_img is None:
                log.warning(f"Comic #{comic_num} not found in database")
                return None

            log.success(f"Found image for XKCD comic #{comic_num} in database.")

            try:
                comic_img: comic.XKCDComicImageOut = comic.XKCDComicImageOut(
                    comic_num=db_comic_img.comic_num, img=db_comic_img.img
                )

                return comic_img
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception converting XKCDComicImageModel to XKCDComicImage class. Details: {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting database connection. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc
