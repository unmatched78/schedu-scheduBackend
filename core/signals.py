import json
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from .models import Shift
from .serializers import ShiftSerializer

@receiver(post_save, sender=Shift)
def broadcast_shift_update(sender, instance, created, **kwargs):
    from .models import Shift
    channel_layer = get_channel_layer()
    serializer = ShiftSerializer(instance)
    data = {
        "type": "shift_update",
        "data": serializer.data,
    }
    # Use async_to_sync to call the asynchronous group send from this synchronous signal.
    async_to_sync(channel_layer.group_send)("shifts", data)
