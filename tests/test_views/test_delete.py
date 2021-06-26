from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from django.urls import include, path, reverse

from rest_fhir.models import Resource


class DeleteAPIViewTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('fhir/', include('rest_fhir.urls')),
    ]

    def test_server_should_410_for_non_version_subsequent_reads(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Organization',
                'name': 'ACME Healthcare Lab',
            }
        )
        instance_url = reverse(
            'read-update-delete',
            kwargs={'type': 'Organization', 'id': str(resource.id)},
        )

        delete_response = self.client.delete(instance_url, format='json')

        self.assertEqual(
            delete_response.status_code, status.HTTP_204_NO_CONTENT
        )

        read_response = self.client.get(instance_url, format='json')
        self.assertEqual(read_response.status_code, status.HTTP_410_GONE)
