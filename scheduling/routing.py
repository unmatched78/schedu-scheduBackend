# scheduling/routing.py
from django.urls import re_path
from .consumers import ShiftConsumer

websocket_urlpatterns = [
    re_path(r'ws/shifts/$', ShiftConsumer.as_asgi()),
]