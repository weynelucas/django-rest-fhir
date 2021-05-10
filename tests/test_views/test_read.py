import calendar

from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from django.urls import path, reverse
from django.urls.conf import include
from django.utils import timezone
from django.utils.http import http_date

from rest_fhir.models import Resource


def to_http_date(dt):
    return http_date(calendar.timegm(dt.utctimetuple()))


class ReadAPIViewTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('fhir/', include('rest_fhir.urls')),
    ]

    def read_resource(self, resource, **kwargs):
        resource_id = str(resource.id)
        resource_type = resource.resource_type

        return self.client.get(
            reverse('read', kwargs={'type': resource_type, 'id': resource_id}),
            **kwargs,
        )

    def test_returned_resouce_shall_have_an_id(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Patient',
                'name': [
                    {'use': 'official', 'text': 'John Doe'},
                ],
            }
        )

        response = self.read_resource(resource)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], str(resource.id))

    def test_returned_resource_shall_have_metadata(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Practitioner',
                'name': [
                    {'use': 'official', 'text': 'Dr Donald Duckles'},
                ],
            }
        )

        response = self.read_resource(resource)

        instant_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
        last_updated = resource.updated_at.strftime(instant_fmt)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('meta', response.data)
        self.assertEqual(
            response.data['meta'],
            {
                'versionId': str(resource.version_id),
                'lastUpdated': last_updated,
            },
        )

    def test_server_should_returns_etag_header_with_version_id(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Organization',
                'name': 'ACME Healthcare Lab',
            }
        )

        response = self.read_resource(resource)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header('ETag'))
        self.assertEqual(response['ETag'], 'W/"%s"' % resource.version_id)

    def test_server_should_returns_last_modified_header(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Organization',
                'name': 'ACME Healthcare Lab',
            }
        )
        last_modified = to_http_date(resource.updated_at)

        response = self.read_resource(resource)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header('Last-Modified'))
        self.assertEqual(response['Last-Modified'], last_modified)

    def test_server_should_returns_404_for_unknown_resource(self):
        # Non-persistent resource
        resource = Resource(resource_type='MedicationRequest')

        response = self.read_resource(resource)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_server_should_returns_410_for_deleted_resource(self):
        resource = Resource(
            resource_type='ServiceRequest',
            deleted_at=timezone.now(),
        )
        resource.save()

        response = self.read_resource(resource)

        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_server_should_returns_304_were_content_unchaged(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Organization',
                'name': 'Health Level Seven International',
                'alias': [
                    'HL7 Internetional',
                ],
            }
        )

        response_if_none_match = self.read_resource(
            resource,
            HTTP_IF_NONE_MATCH='W/"%s"' % resource.version_id,
        )
        response_if_modified_since = self.read_resource(
            resource,
            HTTP_IF_MODIFIED_SINCE=to_http_date(resource.updated_at),
        )

        self.assertEqual(
            response_if_none_match.status_code, status.HTTP_304_NOT_MODIFIED
        )
        self.assertEqual(
            response_if_modified_since.status_code, status.HTTP_304_NOT_MODIFIED
        )
