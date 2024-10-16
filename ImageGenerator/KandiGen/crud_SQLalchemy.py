import logging
from datetime import datetime
from sqlalchemy import (Integer, String, Column, ForeignKey, Text, DateTime,
                        Boolean, create_engine, insert, select, update, delete)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, sessionmaker, Session


class Base(DeclarativeBase):
    pass


def get_metadata(db_='sqlite:///db2.sqlite3'):
    engine_ = create_engine(db_, echo=True, pool_pre_ping=True)
    Base.metadata.create_all(engine_)

    return engine_


def create_stat_SQLalchemy(db_='sqlite:///db.sqlite3'):
    from .utilities import decor_time, fill_in_table_words
    engine = get_metadata(db_)

    session = sessionmaker(bind=engine)
    db = session()
    try:
        if __name__ == '__main__':
            func_ = decor_time()
            func_ = func_(fill_in_table_words)
            func_()
        else:
            fill_in_table_words()
        return True, db
    finally:
        db.close()
        engine.dispose()
    return False, db


class Image(Base):
    __tablename__ = "KandiGen_image"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('KandiGen_usersettings.user_id'), index=True)
    image: Mapped[str] = mapped_column(String, nullable=False)
    query_text: Mapped[str] = mapped_column(Text)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())


    def __str__(self):
        return f"{self.user_id} - {self.image}"


class Word(Base):
    __tablename__ = "KandiGen_word"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    # image = relationship('Image', secondary='KandiGen_word_images', back_populates='words')

    def __str__(self):
        return self.name


class UserSettings(Base):
    __tablename__ = 'KandiGen_usersettings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('auth_users.id'))
    day_team = Column(Boolean, default=True)
    page_num = Column(Integer, default=9)
    age = Column(Integer, default=0)

    def __str__(self):
        return str(self.user_id.username)


class Word_Image(Base):
    __tablename__ = 'KandiGen_word_image'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word_id = Column(Integer, ForeignKey('KandiGen_word.id'))
    image_id = Column(Integer, ForeignKey('KandiGen_image.id'))


def get_images(user_id=None, all_user: bool = False):
    """
    Запрос объектов таблицы Image (картинок) по одному или по всем пользователям
    :param user_id: ID пользователя
    :param all_user: флаг выборки по всем пользователям для галереи
    :return: результат запроса, список объектов таблицы Image
    """
    if all_user:
        images = db.query(Image).all()
    elif user_id:
        images = db.query(Image).filter(Image.user_id == user_id)
    else:
        images = []
    return images


def add_m_m_word_image(word_id: int, image_id: int) -> bool:
    """
    Дополнить связь многие ко многим одним элементом image_id
    :param word_id: слово
    :param image_id: ID картинки
    :return: Успех/неуспех
    """
    try:
        err = db.execute(insert(Word_Image).values(word_id=word_id, image_id=image_id))
        logging.info(f'Добавлена связь Word ({word_id}) - Image ({image_id}): {err}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка связи Word ({word_id}) - Image ({image_id}): {err}')
        return False


def add_word(word: int, image_id=None) -> bool:
    """
    Добавить слово в таблицу Word и заполнить связи Word - Image
    :return: Успех/неуспех
    """
    try:
        err = ''
        try:
            err = db.execute(insert(Word).values(name=word))
            db.commit()
        except Exception as err_:
            logging.info(f'Ошибка добавления слова {word}: {err_}')
        wrd = db.query(Word).filter(Word.name == word).one()
        cnt = wrd.count
        cnt += 1
        db.execute(update(Word).where(Word.name == word).values(count=cnt))
        db.commit()
        err = str(err) + ', количество: ' + str(cnt)
        logging.info(f'Добавлено слово {word}: {err}')
        if not (image_id is None):
            add_m_m_word_image(wrd.id, image_id)
        return True
    except Exception as err:
        logging.exception(f'Ошибка добавления слова {word}: {err}')
        return False


def delete_all_words():
    try:
        i = str(db.execute(delete(Word)))
        i += ' | ' + str(db.execute(delete(Word_Image)))
        db.commit()
        logging.info(f'Удалены все Word: {i}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка удаления Word: {err}')
        return False


def get_all_words():
    """
    Запрос всех слов для статистики
    """
    return db.query(Word).all()


if __name__ == '__main__':
    logging.basicConfig(
        # filename='SQLAlchemy.log', filemode='a', encoding='utf-8',
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        level=logging.INFO)
    rez = create_stat_SQLalchemy('sqlite:///db2.sqlite3')
    db: Session = rez[1]
