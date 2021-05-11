from rest_framework import status
from rest_framework.response import Response

from django.utils.cache import get_conditional_response

from .conditional_read import ConditionalReadMixin


class ReadResourceMixin(ConditionalReadMixin):
    def read(self, request, *args, **kwargs):
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
