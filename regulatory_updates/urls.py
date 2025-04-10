# regulatory_updates/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('updates/', RegulatoryUpdateListAPIView.as_view(), name='list-updates'),
    path('updates/create/', RegulatoryUpdateCreateAPIView.as_view(), name='create-update'),
    path('actions/create/', UpdateActionCreateAPIView.as_view(), name='create-action'),
    path('actions/', UpdateActionListAPIView.as_view(), name='list-actions'),
    path('fetch/', FetchRegulatoryUpdatesAPIView.as_view(), name='fetch-updates'),
]