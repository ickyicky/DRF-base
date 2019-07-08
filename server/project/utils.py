from datetime import datetime

import pytz
from django.conf import settings
from django.utils.timezone import is_naive, make_aware


def make_utc(datetime_):
    if settings.USE_TZ and is_naive(datetime_):
        return make_aware(datetime_, timezone=pytz.timezone(settings.TIME_ZONE))

    return datetime_


def now():
    return make_utc(datetime.utcnow())
