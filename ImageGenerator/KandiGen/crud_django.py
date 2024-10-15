from .models import Image, Word, UserSettings
import logging

TEAM_DEFAULT = False
PAGE_DEFAULT = 9


def get_team_for_user(user_id):
    """
    Возвращает текущую тему (темную - False или светлую - True)
    """
    user_ = UserSettings.objects.filter(user_id=user_id)
    if len(user_) == 0:
        set_team_for_user(user_id, team=TEAM_DEFAULT, check=False)
        return TEAM_DEFAULT
    return user_[0].day_team


def set_team_for_user(user_id, team=TEAM_DEFAULT, check=True):
    """
    Записать в базу новую тему (темную - False или светлую - True)
    """
    try:
        if not check:
            UserSettings.objects.create(user_id=user_id, day_team=team)
            return True
        user_ = UserSettings.objects.filter(user_id=user_id).first()
        if user_:
            user_.day_team = team
            user_.save()
            return True
    except Exception as er:
        logging.exception(f'Ошибка: {er}')
        raise


def get_page_num_for_user(user_id):
    """
    Возвращает текущее число картинок на страницу
    """
    return UserSettings.objects.get(user_id=user_id).page_num


def set_page_num_for_user(user_id, page_num=PAGE_DEFAULT):
    """
    Записать в базу число картинок на страницу
    """
    try:
        UserSettings.objects.filter(user_id=user_id).update(page_num=page_num)
    except Exception as er:
        logging.exception(f'Ошибка: {er}')
        raise


def get_images(user_id=None, all_user: bool = False):
    """
    Запрос объектов таблицы Image (картинок) по одному или по всем пользователям
    :param user_id: ID пользователя
    :param all_user: флаг выборки по всем пользователям для галереи
    :return: результат запроса, список объектов таблицы Image
    """
    if all_user:
        images = Image.objects.all().order_by('-date')
    elif user_id:
        images = Image.objects.filter(user=user_id).order_by('-date')
    else:
        images = []
    return images


def delete_image(image_id) -> bool:
    """
    Удалить картинку image_id из базы
    :return: Успех/неуспех
    """
    try:
        err = Image.objects.get(id=image_id).delete()
        logging.info(f'Удалена картинка {image_id}: {err}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка удаления картинки {image_id}: {err}')
        return False


def add_m_m_word_image(word: str, img: int | list) -> bool:
    """
    Дополнить связь многие ко многим одним элементом image_id
    :param word: слово
    :param img: ID картинки/картинок
    :return: Успех/неуспех
    """
    try:
        if type(img) is list:
            images_lst = img
        else:
            images = Word.objects.get(name=word).image.all()
            images_lst = []
            for image in images:
                images_lst.append(image.id)
            images_lst.append(img)
        err = Word.objects.get(name=word).image.set(images_lst)
        logging.info(f'Добавлена связь Word ({word}) - Image ({img}): {err}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка связи Word ({word}) - Image ({img}): {err}')
        return False


def add_word(word: str, count=0, img: int | list = None) -> bool:
    """
    Добавить слово в таблицу Word и заполнить связи Word - Image
    :param word: слово
    :param count: количество упоминаний
    :param img: ID картинки/картинок
    :return: Успех/неуспех
    """
    try:
        err = ''
        if type(img) is list:
            err = str(Word.objects.create(name=word, count=count))
        else:
            try:
                err = str(Word.objects.create(name=word))
            except Exception as err_:
                logging.info(f'Ошибка добавления слова {word}: {err_}')
            cnt = int(Word.objects.get(name=word).count) + 1
            Word.objects.filter(name=word).update(count=cnt)
        if not (img is None):
            add_m_m_word_image(word, img)
        err += ', количество: ' + str(count)
        logging.info(f'Добавлено слово {word}: {err}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка добавления слова {word}: {err}')
        return False


def delete_all_words():
    try:
        err = Word.objects.all().delete()
        logging.info(f'Удалены все Word: {err}')
        return True
    except Exception as err:
        logging.exception(f'Ошибка удаления Word: {err}')
        return False


def get_all_words():
    """
    Запрос всех слов для статистики с обратной сортировкой
    """
    return Word.objects.all().order_by('-count')
