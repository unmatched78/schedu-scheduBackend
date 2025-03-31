"""
ASGI config for schedu project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedu.settings")

# # application = get_asgi_application()
 
# from channels.routing import ProtocolTypeRouter, URLRouter  
# from core import routing  
# from channels.auth import AuthMiddlewareStack 

# # Get the ASGI application for Django  
# django_asgi_app = get_asgi_application()  

# # Define the application for ASGI protocol  
# application = ProtocolTypeRouter({  
#     "http": get_asgi_application(),  # Handle HTTP requests  
#     "websocket": AuthMiddlewareStack(URLRouter(  
#         routing.websocket_urlpatterns  # Handle WebSocket connections  
#     )
#     )
# })
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedu.settings")
django.setup()  # Ensure Django is fully set up

# Initialize the Django ASGI application so that it can be used by Channels.
django_asgi_app = get_asgi_application()

# Import routing only after Django is set up.
import core.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
