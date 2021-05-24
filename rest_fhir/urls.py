from django.urls import path

from .views import CreateAPIView, ReadAPIView, VReadAPIView

urlpatterns = [
    path('<str:type>/<uuid:id>/', ReadAPIView.as_view(), name='read'),
    path(
        '<str:type>/<uuid:id>/_history/<int:vid>',
        VReadAPIView.as_view(),
        name='vread',
    ),
    path('<str:type>/', CreateAPIView.as_view(), name='create'),
]
