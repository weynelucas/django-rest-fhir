from django.urls import path

from .views import ReadAPIView

urlpatterns = [
    path('<str:type>/<uuid:id>/', ReadAPIView.as_view(), name='read'),
]
