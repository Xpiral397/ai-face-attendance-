from django.urls import re_path
from . import consumers

# WebSocket URL patterns - these will be used in the ASGI application
websocket_urlpatterns = [
    re_path(r'ws/auth/face/$', consumers.FaceAuthConsumer.as_asgi()),
] 