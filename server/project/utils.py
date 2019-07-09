from datetime import datetime

import pytz
from django.conf import settings
from django.utils import timezone


def make_aware(datetime_):
    if settings.USE_TZ and timezone.is_naive(datetime_):
        return timezone.make_aware(
            datetime_, timezone=pytz.timezone(settings.TIME_ZONE)
        )

    return datetime_


def make_naive(datetime_):
    if timezone.is_aware(datetime_):
        return timezone.make_naive(datetime_)

    return datetime_


def make_utc(datetime_):
    datetime_ = make_aware(datetime_)
    return datetime_.astimezone(pytz.utc)


def make_naive_utc(datetime_):
    return make_utc(datetime_).replace(tzinfo=None)


def now():
    return make_aware(datetime.now())
