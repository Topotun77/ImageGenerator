#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

execut_time = {
    'django': 0,
    'django_v2': 0,
    'SQLAlchemy': 0,
    'TortoiseORM': 0,
}

logging.basicConfig(
        filename='kandi_gen.log', filemode='a', encoding='utf-8',
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        level=logging.INFO)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImageGenerator.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()