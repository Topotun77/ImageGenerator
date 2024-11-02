"""
WSGI config for ImageGenerator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import logging

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImageGenerator.settings')

application = get_wsgi_application()

execut_time = {
    'django': 0,
    'django_v2': 0,
    'SQLAlchemy': 0,
    'SQLAlchemy_v2': 0,
    'TortoiseORM': 0,
    'TortoiseORM_v2': 0,
}

logging.basicConfig(
        filename='kandi_gen.log', filemode='a', encoding='utf-8',
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        level=logging.INFO)
