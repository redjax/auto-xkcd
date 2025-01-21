from loguru import logger as log

from celery import current_app, shared_task
import db_lib
from depends import db_depends
from domain import xkcd as xkcd_domain
import xkcdapi
import xkcdapi.controllers
import xkcdapi.db_client


@log.catch
@current_app.task(name="adhoc-current-comic")
def task_adhoc_current_comic() -> dict:
    log.info("Running adhoc Celery task to request current XKCD comic")
    
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController()
    
    try:
        current_comic: xkcd_domain.XkcdComicIn = xkcd_api_controller.get_current_comic()
        if not current_comic:
            log.warning("current_comic is None, indicating an error requesting the comic from the XKCD API.")
            return
        
        log.success("Retrieved current XKCD comic from the XKCD API.")
        
        return current_comic.model_dump()
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting current XKCD comic. Details: {exc}"
        log.error(msg)
        
        raise exc
    

@log.catch
@current_app.task(name="adhoc-request-comic")
def task_adhoc_request_comic(num: int, save: bool = False) -> dict | None:
    if not num:
        raise ValueError("Missing input comic number ('num' param)")
    if num in xkcd_domain.constants.IGNORE_COMIC_NUMS:
        log.warning(f"Comic #{num} is in the list of ignored comic numbers. Skipping.")
        return

    log.info(f"Running adhoc Celery task to request XKCD comic #{num}")
    
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController()
    
    try:
        comic, comic_img = xkcd_api_controller.get_comic_and_img(comic_num=num)

        if not comic:
            log.warning("comic is None, indicating an error requesting the comic from the XKCD API.")
            return
        
        log.success(f"Retrieved XKCD comic #{num} from the XKCD API.")
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting XKCD comic #{num}. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    if not save:
        return comic.model_dump()
    
    log.debug(f"Saving comic #{comic.num} to database.")
    # engine = db_depends.get_db_engine()
    
    db_comic, db_comic_img = xkcdapi.db_client.save_comic_and_img_to_db(comic=comic, comic_img=comic_img)
    log.success(f"Saved comic #{db_comic.num} and its image to the database.")
    
    return comic.model_dump()
