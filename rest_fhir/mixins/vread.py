from .conditional_read import ConditionalReadMixin


class VReadResourceMixin(ConditionalReadMixin):
    def vread(self, request, *args, **kwargs):
        return self.conditional_read(request, *args, **kwargs)
