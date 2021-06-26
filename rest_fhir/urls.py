from django.urls import path

from .views import ReadUpdateDeleteAPIView, SearchCreateAPIView, VReadAPIView

urlpatterns = [
    # Instance Level Interactions
    path(
        '<str:type>/<uuid:id>/',
        ReadUpdateDeleteAPIView.as_view(),
        name='read-update-delete',
    ),
    path(
        '<str:type>/<uuid:id>/_history/<int:vid>',
        VReadAPIView.as_view(),
        name='vread',
    ),
    # Type Level Interactions
    path('<str:type>/', SearchCreateAPIView.as_view(), name='search-create'),
]
