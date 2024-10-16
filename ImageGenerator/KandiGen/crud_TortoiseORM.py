from datetime import datetime
import logging
import asyncio

from tortoise import Tortoise
if __name__ == '__main__':
    from ..models_tortoise import *
else:
    from models_tortoise import *


async def get_generate_schemas(db_url="sqlite:///db2.sqlite3"):
    await Tortoise.init(db_url=db_url,
                        modules={'models': ['models_tortoise']})
    rez = await Tortoise.generate_schemas()
    return rez


def decor_time(crud_func=None):
    """
    Декоратор для вычисления времени работы функции
    :param crud_func: Название фреймворка: 'django', 'SQLAlchemy', 'Tortoise ORM'
    :return: полученную обернутую функцию
    """

    def decor(func):
        async def execution_time(*args, **kwargs):
            rez = False
            start = datetime.now()
            rez = await func(*args, **kwargs)
            end = datetime.now()
            duration = end - start
            str_ = f'Функция {func.__name__}("{crud_func}") выполнялась: {duration}'
            print(str_)
            logging.info(str_)
            return rez

        return execution_time

    return decor


def format_str(text: str) -> str:
    """
    Перевести строку в нижний регистр и удалить лишние символы
    :return: Отформатированная строка
    """
    text = text.lower()
    for i in '?!:;.,$№#%@"~`()[]{}<>/+*':
        text = text.replace(i, '')
    return text


async def fill_in_table_words() -> bool:
    """
    Удалить и заполнить таблицу Word заново
    :return: успех/неудача
    """
    try:
        await delete_all_words()
        images = await get_images(all_user=True)
        for image in images:
            text = format_str(image.query_text)
            for i in text.split(' '):
                await add_word(i, img=image.id)
        return True
    except Exception as err:
        logging.info(f'Ошибка заполнения таблицы Word: {err}')
        return False


async def fill_in_table_words_v2() -> bool:
    """
    Удалить и заполнить таблицу Word заново
    :return: успех/неудача
    """
    word_dict: dict = {}
    try:
        images = await get_images(all_user=True)
        for image in images:
            text = format_str(image.query_text)
            for i in text.split(' '):
                if i in word_dict:
                    word_dict[i][1] += [image.id]
                else:
                    word_dict[i] = [1, [image.id]]
                word_dict[i][0] = len(word_dict[i][1])
        print(word_dict)
        await delete_all_words()
        for word, value in word_dict.items():
            await add_word(word, *value)
        return True
    except Exception as err:
        logging.info(f'Ошибка заполнения таблицы Word: {err}')
        return False


async def create_stat_TortoiseORM(db_url="sqlite://db.sqlite3", module_name='fill_in_table_words_v2'):

    await get_generate_schemas(db_url)
    if __name__ == '__main__':
        func_ = decor_time()
        if module_name == 'fill_in_table_words':
            func_ = func_(fill_in_table_words)
        elif module_name == 'fill_in_table_words_v2':
            func_ = func_(fill_in_table_words_v2)
        await func_()
    else:
        if module_name == 'fill_in_table_words':
            await fill_in_table_words()
        elif module_name == 'fill_in_table_words_v2':
            await fill_in_table_words_v2()

    await Tortoise.close_connections()
    return True


async def get_images(user_id=None, all_user: bool = False):
    """
    Запрос объектов таблицы Image (картинок) по одному или по всем пользователям
    :param user_id: ID пользователя
    :param all_user: флаг выборки по всем пользователям для галереи
    :return: результат запроса, список объектов таблицы Image
    """
    if all_user:
        images = await Image.all()
    elif user_id:
        images = await Image.filter(user_id=user_id)
    else:
        images = []
    return images


async def add_m_m_word_image(word_id: int, img: int | list[int]) -> bool:
    """
    Дополнить связь многие ко многим одним элементом image_id
    :param word_id: слово
    :param img: ID картинки/картинок
    :return: Успех/неуспех
    """
    err = ''
    try:
        if type(img) is list:
            for i in img:
                rez = await Word_Image.update_or_create(word_id=word_id, image_id=i)
                err += ', ' + str(rez)
        else:
            rez = await Word_Image.update_or_create(word_id=word_id, image_id=img)
            err += ', ' + str(rez)
        logging.info(f'Добавлена связь Word ({word_id}) - Image ({img}): {err}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка связи Word ({word_id}) - Image ({img}): {err}')
        return False


async def add_word(word: str, cnt=0, img: int | list[int] = None) -> bool:
    """
    Добавить слово в таблицу Word и заполнить связи Word - Image
    :param word: слово
    :param cnt: количество упоминаний
    :param img: ID картинки/картинок
    :return: Успех/неуспех
    """
    rez, wrd = True, None
    try:
        err = ''
        if type(img) is list:
            wrd = await Word.update_or_create(name=word, count=cnt)
            wrd = wrd[0]
        else:
            wrd = await Word.filter(name=word).first()
            if wrd:
                cnt = wrd.count + 1
                wrd.count = cnt
                await wrd.save()
            else:
                cnt = 1
                wrd = await Word.update_or_create(name=word, count=cnt)
                wrd = wrd[0]
        err = err + str(wrd)
        if img:
            await add_m_m_word_image(wrd.id, img)
        err = err + ', количество: ' + str(cnt)
        logging.info(f'Добавлено слово {word}: {err}')
    except Exception as err_:
        logging.exception(f'Ошибка добавления слова "{word}": {err_}')
        rez = False
    return rez


async def delete_all_words():
    try:
        wrd2 = await Word_Image.all().delete()
        wrd = await Word.all().delete()
        logging.info(f'Удалены все Word: {wrd}, {wrd2}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка удаления Word: {err}')
        return False


async def get_all_words():
    """
    Запрос всех слов для статистики
    """
    words = await Word.all()
    return words


if __name__ == '__main__':
    logging.basicConfig(
        filename='TortoiseORM.log', filemode='a', encoding='utf-8',
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        level=logging.INFO)
    asyncio.run(create_stat_TortoiseORM("sqlite://db.sqlite3", module_name='fill_in_table_words'))
