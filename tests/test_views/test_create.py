from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from django.urls import include, path, reverse

from rest_fhir.models import Resource

from ..utils import to_http_date


class CreateAPIViewTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('fhir/', include('rest_fhir.urls')),
    ]

    def create(self, data={}, **kwargs):
        resource_type = data['resourceType']

        return self.client.post(
            reverse('create', kwargs={'type': resource_type}),
            data=data,
            format='json',
            **kwargs,
        )

    def test_server_should_accept_resource_as_submitted(self):
        request_body = {
            'resourceType': 'Patient',
            'name': [
                {'use': 'official', 'family': 'Donald', 'given': ['Duck']}
            ],
        }

        response = self.create(request_body)

        # Assert resource created with an id
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

        # Assert created resource exists on database as submitted
        resource = Resource.objects.filter(
            resource_type=request_body['resourceType'], id=response.data['id']
        ).first()

        self.assertIsNotNone(resource)
        self.assertEqual(
            resource.resource_content,
            {'id': str(resource.id), **request_body},
        )

    def test_created_resource_shall_ignore_id_from_request_body(self):
        request_body = {
            'resourceType': 'Patient',
            'id': 'pat1',
            'name': [
                {'use': 'official', 'family': 'Donald', 'given': ['Duck']}
            ],
        }

        response = self.create(request_body)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertNotEqual(response.data['id'], request_body['id'])

    def test_created_resource_shall_ignore_meta_from_request_body(self):
        request_body = {
            'resourceType': 'Patient',
            'id': 'pat1',
            'name': [
                {'use': 'usual', 'given': ['Jim']},
            ],
            'meta': {
                'versionId': 'pat1.1',
                'lastUpdated': '2017-01-01T00:00:00Z',
            },
        }

        response = self.create(request_body)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('meta', response.data)
        self.assertIn('versionId', response.data['meta'])
        self.assertIn('versionId', response.data['meta'])
        self.assertNotEqual(
            response.data['meta']['versionId'],
            request_body['meta']['versionId'],
        )
        self.assertIn('lastUpdated', response.data['meta'])
        self.assertNotEqual(
            response.data['meta']['lastUpdated'],
            request_body['meta']['lastUpdated'],
        )

    def test_server_should_returns_location_which_contains_id_and_vid(self):
        request_body = {
            'resourceType': 'Organization',
            'name': 'ACME Healthcare Industries',
        }

        response = self.create(request_body)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.has_header('Location'))
        self.assertTrue(
            response['Location'],
            reverse(
                'vread',
                kwargs={
                    'type': 'Patient',
                    'id': response.data['id'],
                    'vid': response.data['meta']['versionId'],
                },
            ),
        )

    def test_server_should_returns_etag_header_with_version_id(self):
        response = self.create(
            {
                'resourceType': 'Practitioner',
                'name': [
                    {'use': 'official', 'text': 'Juri van Gelder'},
                ],
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.has_header('ETag'))
        self.assertEqual(
            response['ETag'], 'W/"%s"' % response.data['meta']['versionId']
        )

    def test_server_should_returns_last_modified_header(self):
        response = self.create(
            {
                'resourceType': 'Practitioner',
                'name': [
                    {'family': 'Dopplemeyer', 'given': ['Sherry']},
                ],
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.has_header('Last-Modified'))
        self.assertEqual(
            response['Last-Modified'],
            to_http_date(response.data['meta']['lastUpdated']),
        )

    def test_server_should_returns_400_for_failed_fhir_validation_rules(self):
        pass
