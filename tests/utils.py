import calendar

from django.utils.http import http_date


def to_http_date(dt):
    return http_date(calendar.timegm(dt.utctimetuple()))
