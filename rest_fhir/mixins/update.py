from rest_framework import status
from rest_framework.response import Response

from django.http.response import Http404
from django.urls import reverse

from .conditional_read import ConditionalReadMixin


class UpdateResourceMixin(ConditionalReadMixin):
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            # Server should returns HTTP status 201 Created for resources
            # brought back to life after subsequent update interaction over a
            # deleted resource
            # https://www.hl7.org/fhir/http.html#update
            success_status = (
                status.HTTP_201_CREATED
                if instance.deleted_at is not None
                else status.HTTP_200_OK
            )

            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need
                # to forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            headers = self.get_success_headers(serializer.data)
            return Response(
                data=serializer.data, status=success_status, headers=headers
            )

        except Http404:
            return self.update_as_create(request, *args, **kwargs)

    def update_as_create(self, request, *args, **kwargs):
        """
        Update as Create

        Allow clients to PUT a resource to a location that does not yet exist
        on the server - effectively, allowing the client to define the id of the
        resource.

        https://www.hl7.org/fhir/http.html#upsert
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_update(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            ret = dict()
            ret['Location'] = reverse(
                'vread',
                kwargs={
                    'type': data['resourceType'],
                    'id': data['id'],
                    'vid': data['meta']['versionId'],
                },
            )
            ret.update(self.get_conditional_headers(data))
            return ret
        except (TypeError, KeyError):
            return {}
