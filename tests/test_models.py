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
        self.assertEqual(resource.resource_version, 1)
        self.assertEqual(
            resource.resource_version_obj.resource_version,
            resource.resource_version,
        )
        self.assertEqual(
            resource.resource_version_obj.resource_text,
            resource_text_with_id,
        )
        self.assertEqual(
            resource.published_at,
            resource.resource_version_obj.published_at,
        )
        self.assertEqual(
            resource.updated_at,
            resource.resource_version_obj.published_at,
        )

        self.assertEqual(resource.history.count(), 1)
        self.assertEqual(
            resource.resource_version_obj, resource.history.first()
        )

    def test_update_resource(self):
        # Creating the resource
        resource_text = {
            'resourceType': 'Organization',
            'name': 'XYZ Insurance',
            'alias': [
                'ABS Insurance',
            ],
        }
        resource = Resource()
        resource.save(resource_text=resource_text)
        first_version_obj = resource.resource_version_obj

        # Updating the resource
        resource_text_updated = {
            'resourceType': 'Organization',
            'name': 'ACME Healthcare',
            'alias': [
                'ACME',
                'ACME Clinical Lab',
            ],
        }
        resource_text_updated_with_id = {
            'id': str(resource.resource_id),
            **resource_text_updated,
        }
        resource.save(resource_text=resource_text_updated)
        last_version_obj = resource.resource_version_obj

        self.assertIsNotNone(resource.resource_version, 2)
        self.assertEqual(
            last_version_obj.resource_text, resource_text_updated_with_id
        )
        self.assertEqual(resource.published_at, first_version_obj.published_at)
        self.assertEqual(resource.updated_at, last_version_obj.published_at)
        self.assertEqual(resource.history.count(), 2)
        self.assertEqual(first_version_obj, resource.history.first())
        self.assertEqual(last_version_obj, resource.history.last())
