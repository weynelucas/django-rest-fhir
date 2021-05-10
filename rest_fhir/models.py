import uuid

from django.db import models
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

    def save(self, resource_text=None, **kwargs):
        first = self._state.adding
        resource_id = str(self.id)
        resource_text = resource_text and {'id': resource_id, **resource_text}

        self.resource_type = resource_text and resource_text['resourceType']
        super().save(**kwargs)
        self.set_resource_version(resource_text=resource_text, first=first)

    def set_resource_version(self, resource_text=None, first=False):
        version_id = self.version_id + 1
        version = self.history.create(
            version_id=version_id, resource_text=resource_text
        )

        self.version = version
        self.updated_at = version.published_at
        if first:
            self.published_at = version.published_at

        super().save(update_fields=['version_id', 'updated_at', 'published_at'])


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
    resource_text = models.JSONField(
        help_text=_('The actual full text of the resource being stored')
    )
    published_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_(
            'Date that version was created version of the resource was created'
        ),
    )

    class Meta:
        db_table = 'fhir_resource_ver'
        unique_together = ['resource', 'version_id']
        ordering = ['resource', 'version_id']
        verbose_name = 'resource'
        verbose_name_plural = 'resource versions'
