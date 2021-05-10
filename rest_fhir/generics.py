from rest_framework.generics import GenericAPIView

from django.db.models import QuerySet

from .exceptions import Gone
from .models import Resource


class FhirGenericAPIView(GenericAPIView):
    default_queryset = Resource.objects.select_related('version')
    resource_type_url_kwarg = 'type'
    resource_type_field = 'resource_type'
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        queryset = self.queryset

        if queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

        resource_type_url_kwarg = (
            self.resource_type_url_kwarg or self.resource_type_field
        )

        assert resource_type_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.resource_type_field` '
            'attribute on the view correctly.'
            % (self.__class__.__name__, resource_type_url_kwarg)
        )

        filter_kwargs = {
            self.resource_type_field: self.kwargs[resource_type_url_kwarg]
        }

        return self.default_queryset.filter(**filter_kwargs)

    def get_object(self) -> Resource:
        object = super().get_object()

        # A GET for a deleted resource returns a 410 status code
        # https://www.hl7.org/fhir/http.html#read
        if self.request.method == 'GET' and object.deleted_at is not None:
            raise Gone()

        return object
