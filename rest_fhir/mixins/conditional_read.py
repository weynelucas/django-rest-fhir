import calendar
from typing import Union

from django.utils.http import http_date

from ..models import Resource, ResourceVersion

FhirResource = Union[Resource, ResourceVersion]


class ConditionalReadMixin:
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
            etag, last_modified = self.get_conditional_args()

        headers = dict()
        if request.method in ('GET', 'HEAD'):
            if etag:
                headers['ETag'] = etag

            if last_modified:
                headers['Last-Modified'] = http_date(last_modified)

        return headers
