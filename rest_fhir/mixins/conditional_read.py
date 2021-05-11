import calendar
from typing import Union

from rest_framework import status
from rest_framework.response import Response

from django.utils.cache import get_conditional_response
from django.utils.http import http_date

from ..models import Resource, ResourceVersion

FhirResource = Union[Resource, ResourceVersion]


class ConditionalReadMixin:
    def conditional_read(self, request, *args, **kwargs):
        instance = self.get_object()

        # Test If-Modified-Since and If-None-Match preconditions
        # https://www.hl7.org/fhir/http.html#cread
        etag, last_modified = self.get_conditional_args(request, instance)
        response = get_conditional_response(request, etag, last_modified)
        if response is not None:
            return response

        # Set revelant header on the response if request method is safe
        headers = self.get_success_headers(request, etag, last_modified)
        serializer = self.get_serializer(instance)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
            headers=headers,
        )

    def etag_func(self, request, obj: FhirResource) -> str:
        return 'W/"%s"' % obj.version_id

    def last_modified_func(self, request, obj: FhirResource) -> str:
        return calendar.timegm(obj.last_updated.utctimetuple())

    def get_conditional_args(self, request, obj: FhirResource = None):
        etag = self.etag_func(request, obj)
        last_modified = self.last_modified_func(request, obj)
        return (
            etag,
            last_modified,
        )

    def get_success_headers(
        self,
        request,
        etag=None,
        last_modified=None,
        obj: FhirResource = None,
    ):
        if obj and not (etag and last_modified):
            etag, last_modified = self.get_conditional_args(request, obj)

        headers = dict()
        if request.method in ('GET', 'HEAD'):
            if etag:
                headers['ETag'] = etag

            if last_modified:
                headers['Last-Modified'] = http_date(last_modified)

        return headers
