import os
import logging
from datetime import datetime
# from qsstats import QuerySetStats

from django.conf import settings
from django.http import HttpRequest
from .crud_django import (get_team_for_user, set_team_for_user, TEAM_DEFAULT,
                          add_word, delete_all_words, get_images)
from .crud_SQLalchemy import create_stat_SQLalchemy
from . import kandinsky
from __main__ import execut_time


def decor_log(txt=''):
    """
    Декоратор для ведения логирования
    :param txt: Текст для логирования
    :return: полученную обернутую функцию
    """
    def decor(func):
        def log_writer(*args, **kwargs):
            rez = func(*args, **kwargs)
            str_ = f'{txt}: {rez}' if txt else str(rez)
            logging.info(str_)
            return rez

        return log_writer
    return decor


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
            if crud_func == 'django':
                rez = func(*args, **kwargs)
            elif crud_func == 'SQLAlchemy':
                rez = create_stat_SQLalchemy('sqlite:///db.sqlite3')[0]
            elif crud_func == 'TortoiseORM':
                return False
            elif crud_func == 'django_v2':
                rez = fill_in_table_words_v2()
            else:
                rez = func(*args, **kwargs)
            end = datetime.now()
            duration = end - start
            execut_time[crud_func] = duration
            str_ = f'Функция {func.__name__ if func else "от "}("{crud_func}") выполнялась: {duration}'
            print(str_)
            logging.info(str_)
            return rez

        return execution_time
    return decor


def set_team(request: HttpRequest, team=TEAM_DEFAULT):
    set_team_for_user(request.user, team=team)


def check_team(request: HttpRequest):
    """
    Проверка темы (светлая/темная), в случае смены темы - запись в базу новой темы
    :param request: HTTP-запрос
    :return: тема (светлая/темная)
    """
    if not request.user.is_authenticated:
        return TEAM_DEFAULT
    team = get_team_for_user(request.user)
    if request.method == 'GET':
        day = request.GET.get('day')
        if not (day is None) and (str(team) == day):
            team = not team
            set_team(request, team)
    return team


@decor_log('Генерация картинки')
def kandinsky_query(text: str = 'пустота') -> tuple[str, str]:
    """
    Отправка и обработка запроса на генерацию картинки Kandinsky 3.0
    :param text: текст запроса
    :return: картеж, содержащий имя сформированного файла и текст самого запроса
    для логирования
    """
    dir_ = f'{settings.MEDIA_ROOT}/images/{datetime.now().year}_{datetime.now().month}'
    dir_ = dir_.replace("\\", "/")
    try:
        os.mkdir(dir_)
    except FileExistsError:
        print('exist')
    # file_name = await kandinsky.gen(text.replace("\n", " "), dir_)  #TODO асинхронность
    try:
        file_name = kandinsky.gen(text.replace("\n", " "), dir_)
        file_name_cut = '/'.join(file_name.split('/')[-3:])
    except Exception as err:
        logging.exception(err)
        file_name_cut = f'Error: {err.args}'
    return file_name_cut, text


def format_str(text: str) -> str:
    """
    Перевести строку в нижний регистр и удалить лишние символы
    :return: Отформатированная строка
    """
    text = text.lower()
    for i in '?!:;.,$№#%@"~`()[]{}<>/+*':
        text = text.replace(i, '')
    return text


def split_query_into_words(text: str, img: int | list = None):
    """
    Разбить запрос на слова и внести каждое слово в БД, таблица Word
    :param text: текст запроса
    :param img: id картинки/картинок, сгенерированная с этим запросом
    :return: None
    """
    text = format_str(text)
    for i in text.split(' '):
        add_word(i, img=img)


def fill_in_table_words() -> bool:
    """
    Удалить и заполнить таблицу Word заново
    :return: успех/неудача
    """
    try:
        delete_all_words()
        images = get_images(all_user=True)
        for image in images:
            split_query_into_words(image.query_text, image.id)
        return True
    except Exception as err:
        logging.info(f'Ошибка заполнения таблицы Word: {err}')
        return False


def fill_in_table_words_v2() -> bool:
    """
    Удалить и заполнить таблицу Word заново
    :return: успех/неудача
    """
    word_dict: dict = {}
    try:
        images = get_images(all_user=True)
        for image in images:
            text = format_str(image.query_text)
            for i in text.split(' '):
                if i in word_dict:
                    word_dict[i][0] += 1
                    word_dict[i][1] += [image.id,]
                else:
                    word_dict[i] = [1, [image.id,]]
        delete_all_words()
        for word, value in word_dict.items():
            add_word(word, *value)
        return True
    except Exception as err:
        logging.info(f'Ошибка заполнения таблицы Word: {err}')
        return False


def sum_count_word(words) -> int:
    """
    Подсчет суммы упоминаний всех слов из списка words
    :param words: список слов
    :return: сумма слов
    """
    cnt = 0
    for word in words:
        cnt += word.count
    return cnt
