from . import generics, mixins, serializer
from .models import Resource, ResourceVersion


class ReadUpdateDeleteAPIView(
    mixins.ReadResourceMixin,
    mixins.DeleteResourceMixin,
    generics.FhirGenericAPIView,
):
    serializer_class = serializer.ResourceSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Resource.objects.select_related('version').filter(
            resource_type=self.kwargs['type']
        )

    def get(self, request, *args, **kwargs):
        return self.read(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class VReadAPIView(mixins.VReadResourceMixin, generics.FhirGenericAPIView):
    serializer_class = serializer.ResourceSerializer
    lookup_field = 'version_id'
    lookup_url_kwarg = 'vid'

    def get_queryset(self):
        return (
            ResourceVersion.objects.select_related('resource')
            .order_by('version_id')
            .filter(
                resource__resource_type=self.kwargs['type'],
                resource_id=self.kwargs['id'],
            )
        )

    def get(self, request, *args, **kwargs):
        return self.vread(request, *args, **kwargs)


class SearchCreateAPIView(
    mixins.CreateResourceMixin, generics.FhirGenericAPIView
):
    serializer_class = serializer.ResourceSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
