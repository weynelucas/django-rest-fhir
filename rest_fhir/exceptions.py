from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler

from django.utils.translation import gettext_lazy as _


class Gone(APIException):
    status_code = status.HTTP_410_GONE
    default_detail = _('The resource requested is no longer available.')
    default_code = 'gone'


def operation_outcome_exception_handler(exc: APIException, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        data = {
            'resourceType': 'OperationOutcome',
            'issue': [],
        }

        for attr, details in exc.get_full_details().items():
            for detail in details:
                issue = {
                    'severity': 'error',
                    'code': detail.get('code'),
                    'expression': '{}.{}'.format(
                        context['view'].kwargs.get('type', 'Resource'),
                        attr,
                    ),
                    'details': {
                        'text': detail.get('message'),
                    },
                }

                data['issue'].append(issue)

        response.data = data

    return response
