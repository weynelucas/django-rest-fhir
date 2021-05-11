from typing import Union

from rest_framework.generics import GenericAPIView

from .exceptions import Gone
from .models import Resource, ResourceVersion

FhirResource = Union[Resource, ResourceVersion]


class FhirGenericAPIView(GenericAPIView):
    def get_object(self) -> FhirResource:
        object = super().get_object()

        # A GET for a deleted resource returns a 410 status code
        # https://www.hl7.org/fhir/http.html#read
        if self.request.method == 'GET' and object.deleted_at is not None:
            raise Gone()

        return object
