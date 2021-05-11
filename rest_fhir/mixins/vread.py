import calendar

from .read import ReadResourceMixin


class VReadResourceMixin(ReadResourceMixin):
    def vread(self, request, *args, **kwargs):
        return self.read(request, *args, **kwargs)

    def last_modified_func(self, request, obj):
        return calendar.timegm(obj.published_at.utctimetuple())
