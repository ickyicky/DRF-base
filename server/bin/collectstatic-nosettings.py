#!/usr/bin/env python3
#  -*- coding:utf-8 -*-
import argparse
import os
import sys

from django.core.management import execute_from_command_line
from dotenv import load_dotenv


def main(args):
    env_path = os.path.join(os.path.dirname(__file__), args.env_file)

    load_dotenv(
        dotenv_path=env_path, verbose=True,
    )
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arriva.settings")

    execute_from_command_line(["manage.py", "collectstatic", "--no-input"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute collectstatic command using given .env file as settings source.",
    )
    parser.add_argument(
        "-e", "--env-file", required=True, help="Environment file location.", metavar="<file>",
    )
    args = parser.parse_args()

    sys.exit(main(args))
