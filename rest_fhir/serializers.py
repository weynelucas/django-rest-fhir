from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from .models import Resource


class MetaElementSerializer(serializers.Serializer):
    versionId = serializers.CharField(source='version_id')
    lastUpdated = serializers.DateTimeField(source='last_updated')


class ResourceSerializer(serializers.Serializer):
    id = serializers.CharField(
        source='resource_id',
        required=True,
        help_text=_('Logical id of this artifact'),
        error_messages={'required': 'The id element is missing.'},
    )
    meta = MetaElementSerializer(
        source='*',
        read_only=True,
        help_text=_('Metadata about the resource'),
    )

    def validate_id(self, element_id):
        url_id = str(self.context['view'].kwargs.get('id', ''))
        if url_id != element_id:
            raise serializers.ValidationError(
                code='value',
                detail='The id element disagrees with the id in the URL.',
            )

        return element_id

    def to_representation(self, instance):
        ret = instance.resource_content or dict()
        ret.update(super().to_representation(instance))
        return ret

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return {**data, **value}

    def create(self, validated_data):
        resource = Resource(id=validated_data['resource_id'])
        resource.save(resource_content=validated_data)
        return resource

    def update(self, instance: Resource, validated_data):
        instance.save(resource_content=validated_data)
        return instance
