import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Resource(models.Model):
    resource_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    resource_type = models.CharField(
        max_length=45, help_text=_('Contains the resource type (e.g. Patient)')
    )
    resource_version = models.ForeignKey(
        'ResourceVersion',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        db_column='resource_version_id',
        help_text=_('This is the current version ID of the resource'),
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
        resource_id = str(self.resource_id)
        resource_text = resource_text and {'id': resource_id, **resource_text}

        super().save(**kwargs)
        self.set_resource_version(resource_text=resource_text, first=first)

    def set_resource_version(self, resource_text=None, first=False):
        version = self.history.create(resource_text=resource_text)
        self.resource_version = version
        self.updated_at = version.published_at
        if first:
            self.published_at = version.published_at

        super().save(
            update_fields=['resource_version', 'updated_at', 'published_at']
        )


class ResourceVersion(models.Model):
    resource_version = models.AutoField(primary_key=True)
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
        ordering = ['resource_version']
        verbose_name = 'resource'
        verbose_name_plural = 'resource versions'
