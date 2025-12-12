"""
WebSocket consumers for real-time updates
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Product


class InventoryConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time inventory updates
    """

    async def connect(self):
        """
        Called when WebSocket is handshaking as part of initial connection
        """
        # Join inventory group
        self.inventory_group_name = 'inventory_updates'

        await self.channel_layer.group_add(
            self.inventory_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"✅ WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        """
        Called when WebSocket closes for any reason
        """
        # Leave inventory group
        await self.channel_layer.group_discard(
            self.inventory_group_name,
            self.channel_name
        )
        print(f"❌ WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """
        Called when we get a text frame from the client
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')

            if message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'Connection alive'
                }))
            elif message_type == 'request_product':
                # Send specific product data
                product_id = data.get('product_id')
                if product_id:
                    product_data = await self.get_product_data(product_id)
                    await self.send(text_data=json.dumps({
                        'type': 'product_update',
                        'product': product_data
                    }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def inventory_update(self, event):
        """
        Called when a message is sent to the inventory group
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'inventory_update',
            'action': event['action'],
            'product': event['product'],
            'timestamp': event['timestamp']
        }))

    async def product_created(self, event):
        """
        Called when a new product is created
        """
        await self.send(text_data=json.dumps({
            'type': 'product_created',
            'product': event['product'],
            'timestamp': event['timestamp']
        }))

    async def product_updated(self, event):
        """
        Called when a product is updated
        """
        await self.send(text_data=json.dumps({
            'type': 'product_updated',
            'product': event['product'],
            'timestamp': event['timestamp']
        }))

    async def product_sold(self, event):
        """
        Called when a product is sold (stock decreased)
        """
        await self.send(text_data=json.dumps({
            'type': 'product_sold',
            'product': event['product'],
            'timestamp': event['timestamp']
        }))

    async def stock_added(self, event):
        """
        Called when stock is added
        """
        await self.send(text_data=json.dumps({
            'type': 'stock_added',
            'product': event['product'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_product_data(self, product_id):
        """
        Get product data from database
        """
        try:
            product = Product.objects.select_related('brand').get(id=product_id)
            return {
                'id': product.id,
                'name': product.name,
                'barcode': product.barcode,
                'quantity': product.quantity,
                'sell_price': str(product.sell_price),
                'cost_price': str(product.cost_price),
                'category': product.category,
                'brand': product.brand.name if product.brand else None,
                'slug': product.slug,
                'image_url': product.image.url if product.image else None,
            }
        except Product.DoesNotExist:
            return None
