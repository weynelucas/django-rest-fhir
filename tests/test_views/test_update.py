from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from django.urls import include, path, reverse

from rest_fhir.models import Resource


class ReadAPIViewTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('fhir/', include('rest_fhir.urls')),
    ]

    def update(self, resource, **kwargs):
        resource_id = str(resource.id)
        resource_type = resource.resource_type
        return self.client.put(
            reverse(
                'read-update-delete',
                kwargs={'type': resource_type, 'id': resource_id},
            ),
            format='json',
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
        pass

    def test_server_should_returns_etag_header_with_version_id(self):
        pass

    def test_deleted_resource_brought_back_to_life_by_subsequent_update(self):
        pass
