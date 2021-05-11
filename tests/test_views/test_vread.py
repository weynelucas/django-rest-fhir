from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from django.urls import include, path, reverse
from django.utils import timezone

from rest_fhir.models import Resource

from ..utils import to_http_date


class VReadAPIViewTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('fhir/', include('rest_fhir.urls')),
    ]

    def setUp(self):
        resource = Resource(resource_type='MedicationRequest')
        resource.save({'resourceType': 'MedicationRequest', 'status': 'draft'})
        resource.save({'resourceType': 'MedicationRequest', 'status': 'active'})
        resource.history.create(version_id=3, deleted_at=timezone.now())

        [self.previous, self.current, self.deleted] = resource.history.all()

    def vread(self, version, **kwargs):
        resource_type = version.resource.resource_type
        resource_id = version.resource_id
        version_id = version.version_id

        return self.client.get(
            reverse(
                'vread',
                kwargs={
                    'type': resource_type,
                    'id': resource_id,
                    'vid': version_id,
                },
            ),
            **kwargs,
        )

    def test_returned_version_shall_have_an_id_with_value_of_resource_id(self):
        version = self.previous
        response = self.vread(version)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], str(version.resource_id))

    def test_returned_version_shall_have_a_version_id_with_value_of_vid(self):
        version = self.current
        response = self.vread(version)

        instant_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
        last_updated = version.published_at.strftime(instant_fmt)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('meta', response.data)
        self.assertEqual(
            response.data['meta'],
            {
                'versionId': str(version.version_id),
                'lastUpdated': last_updated,
            },
        )

    def test_server_should_returns_etag_header_with_version_id(self):
        version = self.previous
        response = self.vread(version)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header('ETag'))
        self.assertEqual(response['ETag'], 'W/"%s"' % version.version_id)

    def test_server_should_returns_last_modified_header(self):
        version = self.current

        response = self.vread(version)
        last_modified = to_http_date(version.published_at)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header('Last-Modified'))
        self.assertEqual(response['Last-Modified'], last_modified)

    def test_server_should_returns_410_for_deleted_resource(self):
        version = self.deleted
        response = self.vread(version)

        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_server_should_returns_304_were_content_unchaged(self):
        version = self.current
        response_if_none_match = self.vread(
            version,
            HTTP_IF_NONE_MATCH='W/"%s"' % version.version_id,
        )
        response_if_modified_since = self.vread(
            version,
            HTTP_IF_MODIFIED_SINCE=to_http_date(version.published_at),
        )

        self.assertEqual(
            response_if_none_match.status_code, status.HTTP_304_NOT_MODIFIED
        )
        self.assertEqual(
            response_if_modified_since.status_code, status.HTTP_304_NOT_MODIFIED
        )
