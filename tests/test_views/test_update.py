from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from django.urls import include, path, reverse

from rest_fhir.models import Resource


class ReadAPIViewTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('fhir/', include('rest_fhir.urls')),
    ]

    def update(
        self, resource=None, resource_type=None, resource_id=None, **kwargs
    ):
        id = resource_id or str(resource.id)
        type = resource_type or resource.resource_type
        return self.client.put(
            reverse('read-update-delete', kwargs={'type': type, 'id': id}),
            format='json',
            **kwargs,
        )

    def read(self, resource, **kwargs):
        resource_id = str(resource.id)
        resource_type = resource.resource_type

        return self.client.get(
            reverse(
                'read-update-delete',
                kwargs={'type': resource_type, 'id': resource_id},
            ),
            **kwargs,
        )

    def test_server_should_accept_resource_as_submitted(self):
        pass

    def test_request_body_should_have_an_id(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Organization',
                'name': 'ACME Healthcare Lab',
            }
        )

        response = self.update(
            resource=resource,
            data={
                'resourceType': 'Organization',
                'name': 'ACME Laboratory of Healthcare',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'resourceType': 'OperationOutcome',
                'issue': [
                    {
                        'severity': 'error',
                        'code': 'required',
                        'expression': 'Organization.id',
                        'details': {
                            'text': 'The id element is missing.',
                        },
                    }
                ],
            },
        )

    def test_request_body_should_have_an_id_identical_to_the_id_in_url(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Organization',
                'name': 'ACME Healthcare Lab',
            }
        )

        response = self.update(
            resource=resource,
            data={
                'resourceType': 'Organization',
                'id': 'de7aa0f3-ea1a-417b-b370-e914266079c9',
                'name': 'ACME Laboratory of Healthcare',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'resourceType': 'OperationOutcome',
                'issue': [
                    {
                        'severity': 'error',
                        'code': 'value',
                        'expression': 'Organization.id',
                        'details': {
                            'text': 'The id element disagrees with the id in the URL.'
                        },
                    }
                ],
            },
        )

    def test_server_should_ignore_meta_from_request_body(self):
        pass

    def test_server_should_returns_location_which_contains_id_and_vid(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Organization',
                'name': 'Pafaizer',
            }
        )

        response = self.update(
            resource,
            data={
                'resourceType': 'Organization',
                'id': str(resource.id),
                'name': 'Pfizer, Inc.',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header('Location'))
        self.assertTrue(
            response['Location'],
            reverse(
                'vread',
                kwargs={
                    'type': 'Organization',
                    'id': response.data['id'],
                    'vid': response.data['meta']['versionId'],
                },
            ),
        )

    def test_server_should_returns_etag_header_with_version_id(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Patient',
                'name': [
                    {'use': 'official', 'text': 'David Eric Grohl'},
                ],
            }
        )

        response = self.update(
            resource,
            data={
                'resourceType': 'Patient',
                'id': str(resource.id),
                'name': [
                    {'use': 'official', 'text': 'Kurt Donald Cobain'},
                ],
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header('ETag'))
        self.assertEqual(
            response['ETag'], 'W/"%s"' % response.data['meta']['versionId']
        )

    def test_deleted_resource_brought_back_to_life_by_subsequent_update(self):
        resource = Resource()
        resource.save(
            resource_content={
                'resourceType': 'Practitioner',
                'name': [
                    {'use': 'official', 'text': 'Juri van Gelder'},
                ],
            }
        )

        # Read first version
        self.assertEqual(self.read(resource).status_code, status.HTTP_200_OK)

        # Read after delete
        resource.delete()
        self.assertEqual(self.read(resource).status_code, status.HTTP_410_GONE)

        # Resource brought back to life (re-created)
        response = self.update(
            resource=resource,
            data={
                'id': str(resource.id),
                'resourceType': 'Practitioner',
                'name': [
                    {
                        'use': 'official',
                        'text': 'Luigi Maas',
                        'family': 'Maas',
                        'given': ['Luigi'],
                        'prefix': ['Dr.'],
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Read after re-creation
        self.assertEqual(self.read(resource).status_code, status.HTTP_200_OK)

    def test_should_allow_update_as_create(self):
        response = self.update(
            resource_type='Organization',
            resource_id='176914ed-58da-4f49-9f16-aaa743911bb4',
            data={
                'resourceType': 'Organization',
                'id': '176914ed-58da-4f49-9f16-aaa743911bb4',
                'name': 'ACME Laboratory of Healthcare',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_resource = Resource.objects.filter(
            id='176914ed-58da-4f49-9f16-aaa743911bb4'
        ).first()

        self.assertIsNotNone(created_resource)
        self.assertEqual(created_resource.history.count(), 1)
