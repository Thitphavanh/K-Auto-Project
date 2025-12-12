"""
Django signals for sending real-time updates via WebSocket
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Product, Transaction
from datetime import datetime


def send_inventory_update(action, product):
    """
    Send inventory update to WebSocket clients
    """
    channel_layer = get_channel_layer()

    product_data = {
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

    # Send message to inventory group
    async_to_sync(channel_layer.group_send)(
        'inventory_updates',
        {
            'type': action,
            'product': product_data,
            'timestamp': datetime.now().isoformat()
        }
    )


@receiver(post_save, sender=Product)
def product_saved(sender, instance, created, **kwargs):
    """
    Signal when a product is created or updated
    """
    if created:
        send_inventory_update('product_created', instance)
    else:
        send_inventory_update('product_updated', instance)


@receiver(post_save, sender=Transaction)
def transaction_created(sender, instance, created, **kwargs):
    """
    Signal when a transaction is created (product sold or stock added)
    """
    if created:
        if instance.transaction_type == 'OUT':
            # Product sold
            send_inventory_update('product_sold', instance.product)
        elif instance.transaction_type == 'IN':
            # Stock added
            send_inventory_update('stock_added', instance.product)
