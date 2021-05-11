from django.urls import path

from .views import ReadAPIView, VReadAPIView

urlpatterns = [
    path('<str:type>/<uuid:id>/', ReadAPIView.as_view(), name='read'),
    path(
        '<str:type>/<uuid:id>/_history/<int:vid>',
        VReadAPIView.as_view(),
        name='vread',
    ),
]
