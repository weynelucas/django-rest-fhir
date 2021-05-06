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


class ResourceVersion(models.Model):
    resource_version = models.AutoField(primary_key=True)
    resource = models.ForeignKey(
        'Resource',
        on_delete=models.CASCADE,
        related_name='history',
        db_column='resource_id',
    )
    resource_text = models.JSONField(
        help_text=_('The actual full text of the resource being stored.')
    )

    class Meta:
        db_table = 'fhir_resource_ver'
        ordering = ['resource_version']
        verbose_name = 'resource'
        verbose_name_plural = 'resource versions'
