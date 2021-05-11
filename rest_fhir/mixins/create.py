from rest_framework.mixins import CreateModelMixin

from django.urls import reverse

from .conditional_read import ConditionalReadMixin


class CreateResourceMixin(CreateModelMixin, ConditionalReadMixin):
    def get_success_headers(self, data):
        try:
            ret = dict()
            ret['Location'] = reverse(
                'vread',
                kwargs={
                    'type': data['resourceType'],
                    'id': data['id'],
                    'vid': data['meta']['versionId'],
                },
            )
            ret.update(self.get_conditional_headers(data))
            return ret
        except (TypeError, KeyError):
            return {}
