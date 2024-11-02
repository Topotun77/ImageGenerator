import asyncio

from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpRequest
from .forms import ImageGenForm
from . import crud_django
from . import utilities
# from __main__ import execut_time
from ImageGenerator.wsgi import execut_time

# Create your views here.


def start(request: HttpRequest):
    team = utilities.check_team(request)
    context = {'day_team': team}
    status = 400 if 'error' in context else 200
    return render(request, template_name='KandiGen/start.html', context=context, status=status)


def stat(request: HttpRequest):
    team = utilities.check_team(request)
    words = crud_django.get_all_words()
    sum_word = utilities.sum_count_word(words)
    context = {
        'day_team': team,
        'words': words,
        'words_gist': words[:20],
        'sum_word': sum_word,
        **execut_time
    }
    status = 400 if 'error' in context else 200
    return render(request, template_name='KandiGen/stat.html', context=context, status=status)


def gallery(request: HttpRequest):
    team = utilities.check_team(request)
    context = {'day_team': team}
    image_feeds = crud_django.get_images(user_id=request.user, all_user=True)
    cnt = request.GET.get('cnt')
    if not request.user.is_authenticated:
        cnt = crud_django.PAGE_DEFAULT
    elif cnt is None or int(cnt) == 0:
        cnt = crud_django.get_page_num_for_user(request.user)
    else:
        crud_django.set_page_num_for_user(request.user, cnt)
    paginator = Paginator(image_feeds, cnt)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    context = {
        **context,
        'image_feeds': page_obj,
    }
    status = 400 if 'error' in context else 200
    return render(request, template_name='KandiGen/gallery.html', context=context, status=status)


def register(request: HttpRequest):
    team = utilities.check_team(request)
    context = {'day_team': team}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            crud_django.set_team_for_user(user.id, check=False)
            return redirect('gen')
    else:
        form = UserCreationForm()
    context = {
        **context,
        'form': form
    }
    status = 400 if 'error' in context else 200
    return render(request, template_name='KandiGen/register.html', context=context, status=status)


def user_login(request: HttpRequest):
    team = utilities.check_team(request)
    context = {'day_team': team}
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('gen')
    else:
        form = AuthenticationForm()
    context = {
        **context,
        'form': form
    }
    status = 400 if 'error' in context else 200
    return render(request, 'KandiGen/login.html', context=context, status=status)


@login_required
def user_logout(request: HttpRequest):
    logout(request)
    return redirect('login')


@login_required
def gen(request: HttpRequest):
    team = utilities.check_team(request)
    context = {'day_team': team}
    if request.method == 'POST':
        form = ImageGenForm(request.POST)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.image = 'images/gen.jpg'
            image.save()
            file = utilities.kandinsky_query(image.query_text)[0]
            if 'Error:' not in file:
                image.image = file
                image.save()
                utilities.split_query_into_words(image.query_text, image.id)
            else:
                context = {
                    **context,
                    'error_rus': 'Ошибка при генерации изображения ((('
                }
                crud_django.delete_image(image.id)
    else:
        form = ImageGenForm()

    image_feeds = crud_django.get_images(user_id=request.user)
    context = {
        **context,
        'image_feeds': image_feeds,
        'form': form,
    }
    status = 400 if 'error' in context else 200
    return render(request, 'KandiGen/gen.html', context=context, status=status)


@login_required
def del_image(request: HttpRequest):
    team = utilities.check_team(request)
    context = {'day_team': team}
    if request.method == 'POST':
        search_txt = request.POST.get('search_txt')
        if search_txt:
            image_feeds = crud_django.get_images(user_id=request.user, query=search_txt)
            context = {**context, 'query_txt': search_txt}
        else:
            image_feeds = crud_django.get_images(user_id=request.user)
        image_id = request.POST.get('image_del')
        if image_id == 'checked':
            for im in image_feeds:
                image = request.POST.get(f'i{im.id}')
                if image:
                    crud_django.delete_image(im.id)
        else:
            crud_django.delete_image(image_id)
        if not search_txt:
            return redirect('del_image')
    else:
        image_feeds = crud_django.get_images(user_id=request.user)
    context = {
        **context,
        'image_feeds': image_feeds,
    }
    status = 400 if 'error' in context else 200
    return render(request, 'KandiGen/del_image.html', context=context, status=status)


def recreate_stat(request: HttpRequest):
    orm_frame = 'django'
    if request.method == 'GET':
        orm_frame = request.GET.get('orm_frame')
        if not orm_frame:
            orm_frame = 'django'
        func = utilities.decor_time(orm_frame)
        func = func(utilities.fill_in_table_words)
        if 'TortoiseORM' in orm_frame:
            asyncio.run(func())
        else:
            func()
    return redirect('stat')





# # на стороне клиента через шаблонизатор
# # src="{{ url_for('serve_file', filename=current_user.avatar_path) }}"
# # На стороне сервера
# @app.route('/files/<path:filename>')
# def serve_file(filename):
#     file_path = os.path.join(DATA_FOLDER, filename)
#     return send_file(file_path)
# # send_file отдает сам файл в клиента.
