#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back_users.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # If the developer runs `python manage.py runserver` without args,
    # default to 127.0.0.1:8005 instead of Django's 8000.
    if len(sys.argv) >= 2 and sys.argv[1] == 'runserver' and len(sys.argv) == 2:
        sys.argv.append('127.0.0.1:8005')
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
