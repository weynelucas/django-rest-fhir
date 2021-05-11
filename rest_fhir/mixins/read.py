from .conditional_read import ConditionalReadMixin


class ReadResourceMixin(ConditionalReadMixin):
    def read(self, request, *args, **kwargs):
        return self.conditional_read(request, *args, **kwargs)
