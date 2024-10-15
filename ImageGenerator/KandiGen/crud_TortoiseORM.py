from datetime import datetime
import logging
import asyncio

from tortoise.models import Model
from tortoise import fields, Tortoise


class Image(Model):
    id = fields.IntField(pk=True)
    # user_id = fields.ForeignKeyField("UserSettings.user_id")
    user_id = fields.IntField()
    image = fields.CharField(255, null=False)
    query_text = fields.TextField()
    date = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'KandiGen_image'

    def __str__(self):
        return f"{self.user_id} - {self.image}"


class Word(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(100, null=False, unique=True)
    count = fields.IntField(default=0)

    # images = fields.ManyToManyField('Image', related_name='words', through='KandiGen_word_image')

    class Meta:
        table = 'KandiGen_word'

    def __str__(self):
        return self.name


class UserSettings(Model):
    id = fields.IntField(pk=True)
    # user_id = fields.ForeignKeyField("auth.User", related_name='usersettings')
    user_id = fields.IntField()
    day_team = fields.BooleanField(default=True)
    page_num = fields.IntField(default=9)
    age = fields.IntField(default=0)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        table = 'KandiGen_usersettings'


class Word_Image(Model):
    id = fields.IntField(pk=True)
    word_id = fields.IntField()
    image_id = fields.IntField()

    class Meta:
        table = 'KandiGen_word_image'


async def get_generate_schemas(db_url="sqlite://db2.sqlite3"):
    await Tortoise.init(db_url=db_url, modules={'models': ['__main__']}, _create_db=True)
    rez = await Tortoise.generate_schemas()
    return rez


# async def test():
#     await get_generate_schemas()
#     # await Word.create(name="test")
#     wrd = await Word.all()
#     print(wrd[0].name)
#     for i in wrd:
#         print(i.name, i.count)
#     # err = await wrd.save()
#     # print(err)
#     # c = Word.create(name="test")
#     await Tortoise.close_connections()


def format_str(text: str) -> str:
    """
    Перевести строку в нижний регистр и удалить лишние символы
    :return: Отформатированная строка
    """
    text = text.lower()
    for i in '?!:;.,$№#%@"~`()[]{}<>/+*':
        text = text.replace(i, '')
    return text


async def create_stat_TortoiseORM(db_url="sqlite://db.sqlite3", module_name='fill_in_table_words_v2'):
    async def fill_in_table_words() -> bool:
        """
        Удалить и заполнить таблицу Word заново
        :return: успех/неудача
        """
        try:
            await delete_all_words()
            images = await get_images(all_user=True)
            for image in images:
                print(image.query_text)
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
                        word_dict[i][1] += [image.id, ]
                    else:
                        word_dict[i] = [1, [image.id, ]]
                    word_dict[i][0] = len(word_dict[i][1])
            print(word_dict)
            await delete_all_words()
            for word, value in word_dict.items():
                await add_word(word, *value)
            return True
        except Exception as err:
            logging.info(f'Ошибка заполнения таблицы Word: {err}')
            return False

    await get_generate_schemas(db_url)
    if __name__ == '__main__':
        def decor_time(crud_func=None):
            """
            Декоратор для вычисления времени работы функции
            :param crud_func: Название фреймворка: 'django', 'SQLAlchemy', 'Tortoise ORM'
            :return: полученную обернутую функцию
            """

            def decor(func):
                def execution_time(*args, **kwargs):
                    rez = False
                    start = datetime.now()
                    rez = func(*args, **kwargs)
                    end = datetime.now()
                    duration = end - start
                    str_ = f'Функция {func.__name__}("{crud_func}") выполнялась: {duration}'
                    print(str_)
                    logging.info(str_)
                    return rez

                return execution_time

            return decor

        func_ = decor_time()
        func_ = func_(fill_in_table_words)
        await func_()
    else:
        # from .utilities import format_str
        if module_name == 'fill_in_table_words':
            await fill_in_table_words()
        elif module_name == 'fill_in_table_words_v2':
            await fill_in_table_words_v2()

    await Tortoise.close_connections()


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


async def add_m_m_word_image(word_id: int, img: int | list) -> bool:
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
                rez = await Word_Image.create(word_id=word_id, image_id=i)
                err += ', ' + str(rez)
        else:
            rez = await Word_Image.create(word_id=word_id, image_id=img)
            err += ', ' + str(rez)
        logging.info(f'Добавлена связь Word ({word_id}) - Image ({img}): {err}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка связи Word ({word_id}) - Image ({img}): {err}')
        return False


async def add_word(word: str, cnt=0, img: int | list = None) -> bool:
    """
    Добавить слово в таблицу Word и заполнить связи Word - Image
    :param word: слово
    :param cnt: количество упоминаний
    :param img: ID картинки/картинок
    :return: Успех/неуспех
    """
    try:
        err = ''
        if type(img) is list:
            wrd = await Word.update_or_create(name=word, count=cnt)
            err = err + str(wrd)
        else:
            wrd, is_created = await Word.get_or_create(name=word, count=0)
            cnt = wrd.count + 1
            wrd = await Word.update_or_create(name=word, count=cnt)
        err += ', количество: ' + str(cnt)
        logging.info(f'Добавлено слово {word}: {err}')
        if not (img is None):
            await add_m_m_word_image(wrd[0].id, img)
        return True
    except Exception as err_:
        logging.exception(f'Ошибка добавления слова {word}: {err_}')
        return False


async def delete_all_words():
    try:
        wrd = await Word.all()
        img = await Image.all()
        print(img)
        err = await Image.update_or_create(user_id=1, image='i.jpg', query_text='кот в мешке')
        print(err)
        await Word.all().delete()
        logging.info(f'Удалены все Word: {wrd}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка удаления Word: {err}')
        return False


async def get_all_words():
    """
    Запрос всех слов для статистики с обратной сортировкой
    """
    words = await Word.all()
    return words


if __name__ == '__main__':
    logging.basicConfig(
        filename='TortoiseORM.log', filemode='a', encoding='utf-8',
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        level=logging.INFO)
    asyncio.run(create_stat_TortoiseORM("sqlite://db5.sqlite3"))
