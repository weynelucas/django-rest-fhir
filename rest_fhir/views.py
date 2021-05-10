from . import generics, mixins, serializer


class ReadAPIView(mixins.ReadResourceMixin, generics.FhirGenericAPIView):
    serializer_class = serializer.ResourceSerializer

    def get(self, request, *args, **kwargs):
        return self.read(request, *args, **kwargs)
