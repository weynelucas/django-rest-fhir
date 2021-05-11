import calendar

import dateutil.parser

from django.utils.http import http_date


def to_http_date(date_or_datestring):
    dt = date_or_datestring
    if isinstance(date_or_datestring, str):
        dt = dateutil.parser.parse(dt)
    return http_date(calendar.timegm(dt.utctimetuple()))
