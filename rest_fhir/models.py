import uuid
from typing import Dict, Tuple

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Resource(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        help_text=_('The Logical Id of the resource'),
    )
    resource_type = models.CharField(
        max_length=45, help_text=_('Contains the resource type (e.g. Patient)')
    )
    version_id = models.PositiveIntegerField(
        null=True,
        default=0,
        db_column='vid',
        help_text=_('This is the current Version Id of the resource'),
    )
    version = models.ForeignObject(
        'ResourceVersion',
        null=True,
        on_delete=models.DO_NOTHING,
        from_fields=['id', 'version_id'],
        to_fields=['resource_id', 'version_id'],
        related_name='+',
    )
    published_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Date that the first version of the resource was created'),
    )
    updated_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_(
            'Date that the most recent version of the resource was created'
        ),
    )
    deleted_at = models.DateTimeField(
        null=True,
        help_text=_(
            'If the most recent version of the resource is a delete, this '
            'contains the timestamp at which the resource was deleted. '
            'Otherwise, contains NULL'
        ),
    )

    class Meta:
        db_table = 'fhir_resource'
        ordering = ['-published_at', '-updated_at']
        verbose_name = 'resource'
        verbose_name_plural = 'resources'

    @property
    def resource_id(self):
        return self.id

    @property
    def resource_content(self):
        if self.deleted_at is None:
            return self.version.resource_content

    @property
    def last_updated(self):
        return self.updated_at

    def save(self, resource_content=None, **kwargs):
        first = self._state.adding

        # Retrieve type from content and force Logical Id
        if resource_content:
            resource_content = {'id': str(self.id), **resource_content}
            self.resource_type = resource_content['resourceType']

        super().save(**kwargs)

        # Create a history entry from content
        if resource_content:
            self.set_resource_version(
                resource_content=resource_content, first=first
            )

    def delete(
        self, using=None, keep_parents=False
    ) -> Tuple[int, Dict[str, int]]:
        self.set_resource_version(delete=True)

        per_obj_deleted = {}
        per_obj_deleted['rest_fhir.Resource'] = 1
        per_obj_deleted['rest_fhir.ResourceVersion'] = 1
        return (2, per_obj_deleted)

    def set_resource_version(
        self, resource_content=None, first=False, delete=False, **kwargs
    ):
        version_id = self.version_id + 1
        deleted_at = timezone.now() if delete else None
        version = self.history.create(
            version_id=version_id,
            resource_content=resource_content,
            deleted_at=deleted_at,
        )

        self.version = version
        self.updated_at = version.published_at

        if first:
            self.published_at = version.published_at

        if delete:
            self.deleted_at = version.deleted_at

        super().save(
            update_fields=[
                'version_id',
                'updated_at',
                'published_at',
                'deleted_at',
            ],
            **kwargs,
        )


class ResourceVersion(models.Model):
    id = models.AutoField(
        primary_key=True,
        db_column='pid',
        help_text=_('The row Persistent Id'),
    )
    version_id = models.PositiveIntegerField(
        db_column='vid',
        help_text=_(
            'The specific version (starting with 1) of the resource that this '
            'row corresponds to'
        ),
    )
    resource = models.ForeignKey(
        'Resource',
        on_delete=models.CASCADE,
        related_name='history',
        db_column='resource_id',
    )
    resource_content = models.JSONField(
        null=True,
        blank=True,
        help_text=_('The actual full text of the resource being stored'),
    )
    published_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_(
            'Date that version was created version of the resource was created'
        ),
    )
    deleted_at = models.DateTimeField(
        null=True,
        help_text=_(
            'Date that version of the resource marked as delete was created. '
            'Deleted versions of a resource have no content'
        ),
    )

    class Meta:
        db_table = 'fhir_resource_ver'
        unique_together = ['resource', 'version_id']
        ordering = ['resource', 'version_id']
        verbose_name = 'resource'
        verbose_name_plural = 'resource versions'

    @property
    def last_updated(self):
        return self.published_at
