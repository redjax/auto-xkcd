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


def save_comic_to_db(comic: xkcd_domain.XkcdComicIn, session_pool: so.sessionmaker[so.Session] | None = None, engine: sa.Engine | None = None) -> xkcd_domain.XkcdComicOut:
    """Save a single XKCD comic to the database.
    
    Params:
        comic (xkcd_domain.XkcdComicIn): The XkcdComicIn schema for a comic to save to the database.
        session_pool (sqlalchemy.orm.sessionmaker[sqlalchemy.orm.Session]): An initialized SQLAlchemy sessionmaker object. If session_pool=None, a default session pool
            will be initialized from the app's database settings.
        engine (sqlalchemy.Engine): An initialized SQLAlchemy Engine. If engine=None, a default Engine will be initialized from the app's database settings.

    Returns:
        (XkcdComicOut): A schema representing the saved XKCD comic metadata in the database.

    """
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

    
def save_comic_img_to_db(comic_img: xkcd_domain.XkcdComicImgIn, session_pool: so.sessionmaker[so.Session] | None = None, engine: sa.Engine | None = None) -> xkcd_domain.XkcdComicImgOut:
    """Save a single XKCD comic image to the database.
    
    Params:
        comic_img (xkcd_domain.XkcdComicImgIn): The XkcdComicImgIn schema for a comic image to save to the database.
        session_pool (sqlalchemy.orm.sessionmaker[sqlalchemy.orm.Session]): An initialized SQLAlchemy sessionmaker object. If session_pool=None, a default session pool
            will be initialized from the app's database settings.
        engine (sqlalchemy.Engine): An initialized SQLAlchemy Engine. If engine=None, a default Engine will be initialized from the app's database settings.

    Returns:
        (XkcdComicImgOut): A schema representing the saved XKCD comic image in the database.

    """
    if not isinstance(comic_img, xkcd_domain.XkcdComicImgIn):
        raise TypeError(f"comic must be an instance of XkcdComicImgIn. Got: ({type(comic_img)})")
    
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


def save_comic_and_img_to_db(comic: xkcd_domain.XkcdComicIn, comic_img: xkcd_domain.XkcdComicImgIn, session_pool: so.sessionmaker[so.Session] | None = None, engine: sa.Engine | None = None) -> t.Tuple[xkcd_domain.XkcdComicOut | None, xkcd_domain.XkcdComicImgOut | None]:
    """Save a comic and image at the same time."""
    comic: xkcd_domain.XkcdComicOut = save_comic_to_db(comic=comic, session_pool=session_pool, engine=engine)
    comic_img: xkcd_domain.XkcdComicImgOut = save_comic_img_to_db(comic_img=comic_img, session_pool=session_pool, engine=engine)
    
    return comic, comic_img
    

def save_multiple_comics_to_db(comics: list[xkcd_domain.XkcdComicIn], session_pool: so.sessionmaker[so.Session] | None = None, engine: sa.Engine | None = None) -> list[xkcd_domain.XkcdComicOut]:
    """Save multiple XkcdComicIn objects to the database at once.
    
    Params:
        comics (list[XkcdComicIn]): List of XkcdComicIn schemas that will be converted to XkcdComicModel database models (if they do not exist in the database already).
        session_pool (sqlalchemy.orm.sessionmaker[sqlalchemy.orm.Session]): An initialized SQLAlchemy sessionmaker object. If session_pool=None, a default session pool
            will be initialized from the app's database settings.
        engine (sqlalchemy.Engine): An initialized SQLAlchemy Engine. If engine=None, a default Engine will be initialized from the app's database settings.
    
    Returns:
        (list[XkcdComicOut]): A list of XkcdComicOut schemas, converted from models saved to the database.

    """
    if (not comics) or (isinstance(comics, list) and len(comics) == 0):
        raise ValueError("comics should be a list of comics with 1 or more XkcdComicIn objects.")
    
    log.debug(f"Incoming comics: {comics}")
    
    ## List to hold comic numbers that already exist in the database
    existing_comic_nums: list[int] = []

    session_pool: so.sessionmaker[so.Session] = return_session_pool(engine=engine)
    
    try:
        with session_pool() as session:
            repo: xkcd_domain.XkcdComicRepository = xkcd_domain.XkcdComicRepository(session=session)
            
            _comic_nums = [c.num for c in comics]
            log.debug(f"Incoming comic nums: {_comic_nums}")
            
            existing_comics: list[xkcd_domain.XkcdComicModel] | None = repo.get_multiple_by_num(comic_nums=_comic_nums) or []
            if existing_comics:
                log.debug(f"Found [{len(existing_comics)}] comic(s) that already exist in database.")
                
                ## Create list of existing comic numbers
                existing_comic_nums = [c.num for c in existing_comics] or []
                log.debug(f"Existing comic numbers: {existing_comic_nums}")
                
                comics = [c for c in comics if c.num not in existing_comic_nums]
                log.debug(f"Working on [{len(comics)}] comic(s) that do not already exist in the database.")
                
            ## Create models
            comic_db_models: list[xkcd_domain.XkcdComicModel] = []
            for comic in comics:
                comic_model: xkcd_domain.XkcdComicModel = xkcd_domain.XkcdComicModel(**comic.model_dump())
                comic_db_models.append(comic_model)
                
            log.debug(f"Converted [{len(comic_db_models)}] XkcdComicIn object(s) to XkcdComicModel object(s)")
            
            comic_models: list[xkcd_domain.XkcdComicModel] = repo.create_all(comic_db_models) or []
            for c in comic_models:
                session.refresh(c)
                
            log.debug(f"Saved [{len(comic_models)}] comic(s) to database.")

    except Exception as exc:
        msg = f"({type(exc)}) Error saving comic image to database. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    if (not comic_models) or (isinstance(comic_models, list) and len(comic_models) == 0):
        log.warning(f"Comic models list is empty, an error occurred while saving multiple comics to database.")
        
        return
    
    log.debug(f"Saved [{comic_models}] comic(s) to the database.")
    
    comics_out: list[xkcd_domain.XkcdComicOut] = []
    
    for c_model in comic_models:
        c_schema: xkcd_domain.XkcdComicOut = xkcd_domain.XkcdComicOut(**c_model.__dict__)
        comics_out.append(c_schema)
        
    log.debug(f"Converted [{len(comics_out)}] comic model(s) to XkcdComicOut object(s)")
    
    return comics_out
    
    
def save_multiple_comic_imgs_to_db(comic_imgs: list[xkcd_domain.XkcdComicImgIn], session_pool: so.sessionmaker[so.Session] | None = None, engine: sa.Engine | None = None) -> list[xkcd_domain.XkcdComicImgOut]:
    """Save multiple XkcdComicImgIn objects to the database at once.
    
    Params:
        comic_imgs (list[XkcdComicImgIn]): List of XkcdComicImgIn schemas that will be converted to XkcdComicImageModel database models (if they do not exist in the database already).
        session_pool (sqlalchemy.orm.sessionmaker[sqlalchemy.orm.Session]): An initialized SQLAlchemy sessionmaker object. If session_pool=None, a default session pool
            will be initialized from the app's database settings.
        engine (sqlalchemy.Engine): An initialized SQLAlchemy Engine. If engine=None, a default Engine will be initialized from the app's database settings.
    
    Returns:
        (list[XkcdComicImgOut]): A list of XkcdComicImgOut schemas, converted from models saved to the database.

    """
    if (not comic_imgs) or (isinstance(comic_imgs, list) and len(comic_imgs) == 0):
        raise ValueError("comic_imgs should be a list of comic images with 1 or more XkcdComicImageIn objects.")
    
    log.debug(f"Incoming comic images: {comic_imgs}")
    
    ## List to hold comic numbers that already exist in the database
    existing_comic_img_nums: list[int] = []

    session_pool: so.sessionmaker[so.Session] = return_session_pool(engine=engine)
    
    try:
        with session_pool() as session:
            repo: xkcd_domain.XkcdComicImageRepository = xkcd_domain.XkcdComicImageRepository(session=session)
            
            _comic_img_nums = [c.num for c in comic_imgs]
            log.debug(f"Incoming comic image nums: {_comic_img_nums}")
            
            existing_comic_imgs: list[xkcd_domain.XkcdComicImageModel] | None = repo.get_multiple_by_num(comic_nums=_comic_img_nums) or []
            if existing_comic_imgs:
                log.debug(f"Found [{len(existing_comic_imgs)}] comic image(s) that already exist in database.")
                
                ## Create list of existing comic image numbers
                existing_comic_img_nums = [c.num for c in existing_comic_imgs] or []
                log.debug(f"Existing comic image numbers: {existing_comic_img_nums}")
                
                comic_imgs = [c for c in comic_imgs if c.num not in existing_comic_img_nums]
                log.debug(f"Working on [{len(comic_imgs)}] comic image(s) that do not already exist in the database.")
                
            ## Create models
            comic_img_db_models: list[xkcd_domain.XkcdComicImageModel] = []
            for comic_img in comic_imgs:
                comic_img_model: xkcd_domain.XkcdComicImageModel = xkcd_domain.XkcdComicImageModel(**comic_img.model_dump())
                comic_img_db_models.append(comic_img_model)
                
            log.debug(f"Converted [{len(comic_img_db_models)}] XkcdComicImgIn object(s) to XkcdComicImageModel object(s)")
            
            comic_img_models: list[xkcd_domain.XkcdComicImageModel] = repo.create_all(comic_img_db_models) or []
            for c in comic_img_models:
                session.refresh(c)
                
            log.debug(f"Saved [{len(comic_img_models)}] comic image(s) to database.")

    except Exception as exc:
        msg = f"({type(exc)}) Error saving comic image to database. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    if (not comic_img_models) or (isinstance(comic_img_models, list) and len(comic_img_models) == 0):
        log.warning(f"Comic image models list is empty, an error occurred while saving multiple comic images to database.")
        
        return
    
    log.debug(f"Saved [{comic_img_models}] comic image(s) to the database.")
    
    comic_imgs_out: list[xkcd_domain.XkcdComicImgOut] = []
    
    for c_i_model in comic_img_models:
        c_schema: xkcd_domain.XkcdComicImgOut = xkcd_domain.XkcdComicImgOut(**c_i_model.__dict__)
        comic_imgs_out.append(c_schema)
        
    log.debug(f"Converted [{len(comic_imgs_out)}] comic image model(s) to XkcdComicImgOut object(s)")
    
    return comic_imgs_out


def save_multiple_comics_and_imgs_to_db(comics: list[xkcd_domain.XkcdComicIn], comic_imgs: list[xkcd_domain.XkcdComicImgIn], session_pool: so.sessionmaker[so.Session] | None = None, engine: sa.Engine | None = None) -> t.Tuple[list[xkcd_domain.XkcdComicOut] | None, list[xkcd_domain.XkcdComicImgOut] | None]:
    """Save a comic and image at the same time."""
    comics: list[xkcd_domain.XkcdComicOut] = save_multiple_comics_to_db(comics=comics, session_pool=session_pool, engine=engine)
    comic_imgs: list[xkcd_domain.XkcdComicImgOut] = save_multiple_comic_imgs_to_db(comic_imgs=comic_imgs, session_pool=session_pool, engine=engine)
    
    return comics, comic_imgs
