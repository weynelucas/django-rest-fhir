from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from .models import Resource


class MetaElementSerializer(serializers.ModelSerializer):
    versionId = serializers.CharField(source='version_id')
    lastUpdated = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = Resource
        fields = ('versionId', 'lastUpdated')


class ResourceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True,
        help_text=_('Logical id of this artifact'),
    )
    meta = MetaElementSerializer(
        source='*',
        read_only=True,
        help_text=_('Metadata about the resource'),
    )

    def to_representation(self, instance):
        ret = instance.version.resource_content or dict()
        ret.update(super().to_representation(instance))
        return ret

    class Meta:
        model = Resource
        fields = ('id', 'meta')
