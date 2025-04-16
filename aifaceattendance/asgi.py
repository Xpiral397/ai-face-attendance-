"""
ASGI config for aifaceattendance project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import authentication.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aifaceattendance.settings')

# Initialize Django ASGI application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Django's ASGI application for handling HTTP requests
    "http": django_asgi_app,
    
    # WebSocket handler with auth and routing
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                authentication.routing.websocket_urlpatterns
            )
        )
    ),
}) 