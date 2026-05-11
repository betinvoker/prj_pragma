#!/usr/bin/env python
"""Django manage.py skeleton for digital_office project."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digital_office.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
