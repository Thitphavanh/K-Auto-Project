"""
WebSocket routing configuration for K-Auto
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket for real-time inventory updates
    re_path(r'ws/inventory/$', consumers.InventoryConsumer.as_asgi()),
]
