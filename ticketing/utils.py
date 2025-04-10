# # ticketing/utils.py
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# from .models import Notification

# def send_automatic_notification(users, message, ticket=None, group=None):
#     channel_layer = get_channel_layer()
#     for user in users:
#         notification = Notification.objects.create(
#             user=user,
#             ticket=ticket,
#             message=message,
#             is_automatic=True
#         )
#         target_group = group if group else f"user_{user.id}"
#         async_to_sync(channel_layer.group_send)(
#             target_group,
#             {
#                 'type': 'send_notification',
#                 'notification_id': notification.id,
#                 'message': notification.message,
#                 'ticket_id': ticket.id if ticket else None,
#                 'created_at': notification.created_at.isoformat(),
#                 'is_read': notification.is_read,
#                 'is_automatic': True
#             }
#         )
# ticketing/utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def send_automatic_notification(users, message, ticket=None, group=None):
    channel_layer = get_channel_layer()
    for user in users:
        notification = Notification.objects.create(
            user=user,
            ticket=ticket,
            message=message,
            is_automatic=True
        )
        target_group = group if group else f"user_{user.id}"
        async_to_sync(channel_layer.group_send)(
            target_group,
            {
                'type': 'send_notification',
                'notification_id': notification.id,
                'message': notification.message,
                'ticket_id': ticket.id if ticket else None,
                'created_at': notification.created_at.isoformat(),
                'is_read': notification.is_read,
                'is_automatic': True
            }
        )