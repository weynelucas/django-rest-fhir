import calendar
from typing import Union

import dateutil.parser
from rest_framework import status
from rest_framework.response import Response

from django.utils.cache import get_conditional_response
from django.utils.http import http_date

from ..models import Resource, ResourceVersion

FhirResource = Union[Resource, ResourceVersion]


class ConditionalReadMixin:
    def conditional_read(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        res_data = serializer.data

        # Test If-Modified-Since and If-None-Match preconditions
        # https://www.hl7.org/fhir/http.html#cread
        etag, last_modified = self.get_conditional_args(res_data)
        response = get_conditional_response(request, etag, last_modified)
        if response is not None:
            return response

        # Set revelant header on the response if request method is safe
        headers = self.get_conditional_headers(res_data)

        return Response(
            data=res_data,
            status=status.HTTP_200_OK,
            headers=headers,
        )

    def etag_func(self, data) -> str:
        return 'W/"%s"' % data['meta']['versionId']

    def last_modified_func(self, data) -> str:
        dt = dateutil.parser.parse(data['meta']['lastUpdated'])
        return calendar.timegm(dt.utctimetuple())

    def get_conditional_args(self, data: dict):
        etag = self.etag_func(data)
        last_modified = self.last_modified_func(data)
        return (
            etag,
            last_modified,
        )

    def get_conditional_headers(self, data):
        etag, last_modified = self.get_conditional_args(data)

        headers = dict()
        if etag:
            headers['ETag'] = etag

        if last_modified:
            headers['Last-Modified'] = http_date(last_modified)

        return headers
