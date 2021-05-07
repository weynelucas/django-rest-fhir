from django.test import TestCase

from rest_fhir.models import Resource


class ResourceTestCase(TestCase):
    def test_create_resource(self):
        resource_text = {
            'resourceType': 'Patient',
            'name': [
                {
                    'use': 'official',
                    'family': 'Donald',
                    'given': [
                        'Duck',
                    ],
                }
            ],
        }

        resource = Resource()
        resource.save(resource_text=resource_text)

        resource_text_with_id = {
            'id': str(resource.resource_id),
            **resource_text,
        }

        self.assertEqual(resource.resource_type, 'Patient')
        self.assertIsNotNone(resource.resource_version_id)
        self.assertEqual(
            resource.resource_version.resource_text,
            resource_text_with_id,
        )
        self.assertEqual(
            resource.published_at,
            resource.resource_version.published_at,
        )
        self.assertEqual(
            resource.updated_at,
            resource.resource_version.published_at,
        )

        self.assertEqual(resource.history.count(), 1)
        self.assertEqual(resource.resource_version, resource.history.first())
