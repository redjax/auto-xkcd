from loguru import logger as log

import typing as t
import db_lib
from depends import db_depends

import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy.exc as sa_exc

from domain import xkcd as xkcd_domain

def return_session_pool(engine: sa.Engine) -> so.sessionmaker[so.Session]:
    if engine is None:
        engine = db_depends.get_db_engine()

    return db_depends.get_session_pool(engine=engine)


def save_comic_to_db(comic: xkcd_domain.XkcdComicIn, session_pool: so.sessionmaker[so.Session] | None = None, engine: sa.Engine | None = None):
    if not isinstance(comic, xkcd_domain.XkcdComicIn):
        raise TypeError(f"comic must be an instance of XkcdComicIn. Got: ({type(comic)})")
    
    session_pool: so.sessionmaker[so.Session] = return_session_pool(engine=engine)
        
    try:
        with session_pool() as session:
            repo: xkcd_domain.XkcdComicRepository = xkcd_domain.XkcdComicRepository(session=session)
            
            existing_comic: xkcd_domain.XkcdComicModel | None = repo.get_by_num(comic_num=comic.num)
            
            if existing_comic:
                log.debug(f"Comic #{comic.num} already exists in database. Returning object from database.")
                return xkcd_domain.XkcdComicOut(**existing_comic.__dict__)
            
            log.debug(f"Did not find comic #{comic.num} in database. Initializing database model")
            
            comic_model: xkcd_domain.XkcdComicModel = xkcd_domain.XkcdComicModel(**comic.model_dump())
            
            log.debug(f"Saving comic: {comic}")
            db_comic: xkcd_domain.XkcdComicModel = repo.create(comic_model)
            session.refresh(db_comic)

    except Exception as exc:
        msg = f"({type(exc)}) Error saving comic to database. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    if not db_comic:
        raise ValueError("db_comic should not have been none, a database error occurred while saving new comic.")
    
    log.debug(f"Converting db comic to XkcdComicOut.")
    log.debug(f"Database model: {db_comic.__dict__}")
    
    comic_out: xkcd_domain.XkcdComicOut = xkcd_domain.XkcdComicOut(**db_comic.__dict__)
    
    return comic_out

    
def save_comic_img_to_db(comic_img: xkcd_domain.XkcdComicImgIn, session_pool: so.sessionmaker[so.Session] | None = None, engine: sa.Engine | None = None):
    if not isinstance(comic_img, xkcd_domain.XkcdComicImgIn):
        raise TypeError(f"comic must be an instance of XkcdComicImgIn. Got: ({type(comic)})")
    
    session_pool: so.sessionmaker[so.Session] = return_session_pool(engine=engine)
        
    try:
        with session_pool() as session:
            repo: xkcd_domain.XkcdComicImageRepository = xkcd_domain.XkcdComicImageRepository(session=session)
            
            existing_comic_img: xkcd_domain.XkcdComicImageModel | None = repo.get_by_num(comic_num=comic_img.num)
            
            if existing_comic_img:
                log.debug(f"Image for comic #{comic_img.num} already exists in database. Returning object from database.")
                return xkcd_domain.XkcdComicImgOut(**existing_comic_img.__dict__)
            
            log.debug(f"Did not find image for comic #{comic_img.num} in database. Initializing database model")
            
            comic_img_model: xkcd_domain.XkcdComicImageModel = xkcd_domain.XkcdComicImageModel(**comic_img.model_dump())
            
            log.debug(f"Saving image for comic: {comic_img}")
            db_comic_img: xkcd_domain.XkcdComicImageModel = repo.create(comic_img_model)
            session.refresh(db_comic_img)

    except Exception as exc:
        msg = f"({type(exc)}) Error saving comic image to database. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    if not db_comic_img:
        raise ValueError("db_comic_img should not have been none, a database error occurred while saving new comic image.")
    
    log.debug(f"Converting db comic image to XkcdComicImgOut.")
    log.debug(f"Database model: {db_comic_img.__repr__()}")
    
    comic_img_out: xkcd_domain.XkcdComicImgOut = xkcd_domain.XkcdComicImgOut(**db_comic_img.__dict__)
    
    return comic_img_out
    

def save_multiple_comics_to_db():
    ...
    
    
def save_multiple_comic_imgs_to_db():
    ...
    
