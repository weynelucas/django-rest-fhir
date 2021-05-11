from rest_framework import serializers

from django.utils.translation import gettext_lazy as _


class MetaElementSerializer(serializers.Serializer):
    versionId = serializers.CharField(source='version_id')
    lastUpdated = serializers.DateTimeField(source='last_updated')


class ResourceSerializer(serializers.Serializer):
    id = serializers.CharField(
        source='resource_id',
        read_only=True,
        help_text=_('Logical id of this artifact'),
    )
    meta = MetaElementSerializer(
        source='*',
        read_only=True,
        help_text=_('Metadata about the resource'),
    )

    def to_representation(self, instance):
        ret = instance.resource_content or dict()
        ret.update(super().to_representation(instance))
        return ret
