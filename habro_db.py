from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from habro_models import Base


class HabroDB:

    def __init__(self, bd_link):
        engine = create_engine(bd_link)
        Base.metadata.create_all(engine)
        self.__session_db = sessionmaker(bind=engine)

    def get_session(self) -> Session:
        return self.__session_db()

    @staticmethod
    def get_or_update(session, model):
        try:
            session.add(model)
            session.commit()
        except Exception as _:
            session.rollback()
            model = session.query(type(model)).filter(type(model).url == model.url).first()
        return model

    def add_post(self, post_obj):
        session = self.get_session()
        post_obj.writer = self.get_or_update(session, post_obj.writer)
        post_obj.tag = [self.get_or_update(session, itm) for itm in post_obj.tag]

        try:
            session.add(post_obj)
            session.commit()
        except Exception as e:
            print(e)
        finally:
            session.close()
