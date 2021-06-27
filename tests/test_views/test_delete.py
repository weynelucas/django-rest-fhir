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

        delete_res = self.client.delete(instance_url, format='json')
        self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(delete_res.data)

        # Non-version specific reads
        read_res = self.client.get(instance_url, format='json')
        self.assertEqual(read_res.status_code, status.HTTP_410_GONE)

        # Version specific reads
        def vread_url(vid):
            return reverse(
                'vread',
                kwargs={
                    'type': 'Organization',
                    'id': str(resource.id),
                    'vid': vid,
                },
            )

        self.assertEqual(resource.history.count(), 2)

        [first_vid, deleted_vid] = resource.history.values_list(
            'version_id', flat=True
        )

        vread_res = self.client.get(vread_url(first_vid))
        self.assertEqual(vread_res.status_code, status.HTTP_200_OK)

        vread_deleted_res = self.client.get(vread_url(deleted_vid))
        self.assertEqual(vread_deleted_res.status_code, status.HTTP_410_GONE)
