from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Post, Writer

if __name__ == '__main__':
    engine = create_engine('sqlite:///gb_blog.db')
    Base.metadata.create_all(engine)

    session_db = sessionmaker(bind=engine)

    session = session_db()

    writers = [Writer(f'name {itm}', f'url/{itm}') for itm in range(1, 30)]
    # for itm in writers:
    #     session.add(itm)
    session.add_all(writers)
    try:
        session.commit()
    except Exception as e:
        print(e)
        # session.rollback()
    finally:
        # session.close()
        pass
    print(1)
