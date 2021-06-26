from django.test import TestCase

from rest_fhir.models import Resource


class ResourceTestCase(TestCase):
    def test_create_resource(self):
        resource_content = {
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
        resource.save(resource_content=resource_content)

        resource_content_with_id = dict(
            id=str(resource.id),
            **resource_content,
        )

        self.assertEqual(resource.resource_type, 'Patient')
        self.assertEqual(resource.version_id, 1)
        self.assertEqual(resource.version.version_id, resource.version_id)
        self.assertEqual(
            resource.version.resource_content, resource_content_with_id
        )
        self.assertEqual(resource.published_at, resource.version.published_at)
        self.assertEqual(resource.updated_at, resource.version.published_at)

        self.assertEqual(resource.history.count(), 1)
        self.assertEqual(resource.version, resource.history.first())

    def test_update_resource(self):
        # Creating the resource
        resource_content = {
            'resourceType': 'Organization',
            'name': 'XYZ Insurance',
            'alias': [
                'ABS Insurance',
            ],
        }
        resource = Resource()
        resource.save(resource_content=resource_content)
        first_version_obj = resource.version

        # Updating the resource
        resource_content_updated = {
            'resourceType': 'Organization',
            'name': 'ACME Healthcare',
            'alias': [
                'ACME',
                'ACME Clinical Lab',
            ],
        }
        resource_content_updated_with_id = dict(
            id=str(resource.id),
            **resource_content_updated,
        )
        resource.save(resource_content=resource_content_updated)
        last_version_obj = resource.version

        self.assertIsNotNone(resource.version_id, 2)
        self.assertEqual(
            last_version_obj.resource_content, resource_content_updated_with_id
        )
        self.assertEqual(resource.published_at, first_version_obj.published_at)
        self.assertEqual(resource.updated_at, last_version_obj.published_at)
        self.assertEqual(resource.history.count(), 2)
        self.assertEqual(first_version_obj, resource.history.first())
        self.assertEqual(last_version_obj, resource.history.last())

    def test_delete_resource(self):
        resource_content = {
            'resourceType': 'Location',
            'name': 'South Wing, second floor',
            'description': 'Second floor of the Old South Wing, formerly in use by Psychiatry',
        }

        resource = Resource()
        resource.save(resource_content=resource_content)
        version = resource.version

        num_objs_deleted, per_obj_deleted = resource.delete()

        self.assertEqual(num_objs_deleted, 2)
        self.assertEqual(
            per_obj_deleted,
            {
                'rest_fhir.Resource': 1,
                'rest_fhir.ResourceVersion': 1,
            },
        )

        self.assertIsNotNone(resource.deleted_at)
        self.assertEqual(resource.history.count(), 2)

        [first_version, deleted_version] = resource.history.all()

        self.assertEqual(version, first_version)
        self.assertIsNotNone(deleted_version.deleted_at)
        self.assertIsNone(deleted_version.resource_content)
        self.assertIsNotNone(resource.deleted_at, deleted_version.deleted_at)
