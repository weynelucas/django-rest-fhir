from rest_framework import status
from rest_framework.exceptions import APIException

from django.utils.translation import gettext_lazy as _


class Gone(APIException):
    status_code = status.HTTP_410_GONE
    default_detail = _('The resource requested is no longer available.')
    default_code = 'gone'
