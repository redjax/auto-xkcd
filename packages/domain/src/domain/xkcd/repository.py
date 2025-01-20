from loguru import logger as log
import typing as t

import db_lib
from .models import XkcdComicImageModel, XkcdComicModel, XkcdCurrentComicMetadataModel

import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy.exc as sa_exc


class XkcdComicRepository(db_lib.base.BaseRepository[XkcdComicModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, XkcdComicModel)
        
    def get_by_num(self, comic_num: int) -> XkcdComicModel | None:
        return self.session.query(XkcdComicModel).filter(XkcdComicModel.num == comic_num).one_or_none()
    
    def get_multiple_by_num(self, comic_nums: list[int]) -> list[XkcdComicModel] | None:
        return self.session.query(XkcdComicModel).filter(XkcdComicModel.num.in_(comic_nums)).all()


class XkcdComicImageRepository(db_lib.base.BaseRepository[XkcdComicModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, XkcdComicImageModel)
        
    def get_by_num(self, comic_num: int) -> XkcdComicImageModel | None:
        return self.session.query(XkcdComicImageModel).filter(XkcdComicImageModel.num == comic_num).one_or_none()

    def get_multiple_by_num(self, comic_nums: list[int]) -> list[XkcdComicImageModel] | None:
        return self.session.query(XkcdComicImageModel).filter(XkcdComicImageModel.num.in_(comic_nums)).all()
    
    
class XkcdCurrentComicMetadataRepository(db_lib.base.BaseRepository[XkcdCurrentComicMetadataModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, XkcdCurrentComicMetadataModel)

    def create_or_update(self, comic_metadata: XkcdCurrentComicMetadataModel) -> XkcdCurrentComicMetadataModel:
        existing_entity: XkcdCurrentComicMetadataModel | None = self.session.query(XkcdCurrentComicMetadataModel).filter(XkcdCurrentComicMetadataModel.id == 1).first()
        # log.debug(f"Existing metadata object: {existing_entity.__dict__}")
        
        if existing_entity:
            log.debug("Current comic metadata already exists in database. Updating existing entity.")
            # log.debug(f"Re-print existing metadata object: {existing_entity.__dict__}")
            
            existing_entity.num = comic_metadata.num
            existing_entity.last_updated = comic_metadata.last_updated
            # log.debug(f"Existing entity after update: {existing_entity}")
            
            self.create(obj=existing_entity)
            # log.debug(f"Existing entity: {existing_entity.__dict__}")
            
            return existing_entity
        else:
            ## Add new entity
            db_comic_metadata: XkcdCurrentComicMetadataModel = self.create(comic_metadata)
            
            return db_comic_metadata
