"""
URL configuration for ImageGenerator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (start, user_login, user_logout, register, gallery, gen, stat,
                    recreate_stat, del_image)

urlpatterns = [
    path('', start, name='start'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    path('gallery/', gallery, name='gallery'),
    path('gen/', gen, name='gen'),
    path('del_image/', del_image, name='del_image'),
    path('create_stat/', recreate_stat, name='recreate_stat'),
    path('stat/', stat, name='stat'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
