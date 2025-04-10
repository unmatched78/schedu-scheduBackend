"""
ASGI config for schedu project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os
# import django
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedu.settings")
# django.setup()  # Ensure Django is fully set up

# # Initialize the Django ASGI application so that it can be used by Channels.
# django_asgi_app = get_asgi_application()

# # Import routing only after Django is set up.
# import core.routing

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             core.routing.websocket_urlpatterns
#         )
#     ),
# })
# project/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django
# Set the settings module and initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedu.settings')
django.setup()  # This ensures apps are loaded
import scheduling.routing #import websocket_urlpatterns
import ticketing.routing 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ticketing.routing.websocket_urlpatterns + scheduling.routing.websocket_urlpatterns
        )
    ),
})