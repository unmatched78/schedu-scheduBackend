# # ticketing/consumers.py
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# import json
# from ticketing.models import Notification
# from scheduling.models import Organization, Department

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope['user']
#         if self.user.is_anonymous:
#             await self.close(code=4001)
#             return
        
#         self.user_group = f"user_{self.user.id}"
#         await self.channel_layer.group_add(self.user_group, self.channel_name)
#         self.groups = [self.user_group]
#         await self.channel_layer.group_add('global', self.channel_name)
#         self.groups.append('global')

#         if self.user.organization:
#             org_group = f"org_{self.user.organization.id}"
#             await self.channel_layer.group_add(org_group, self.channel_name)
#             self.groups.append(org_group)

#         if hasattr(self.user, 'worker_profile') and self.user.worker_profile.department:
#             dept_group = f"dept_{self.user.worker_profile.department.id}"
#             await self.channel_layer.group_add(dept_group, self.channel_name)
#             self.groups.append(dept_group)

#         await self.accept()
#         await self.send_unread_notifications()

#     async def disconnect(self, close_code):
#         for group in getattr(self, 'groups', []):
#             await self.channel_layer.group_discard(group, self.channel_name)

#     async def receive(self, text_data):
#         try:
#             data = json.loads(text_data)
#             action = data.get('action')
#             if action == 'mark_read':
#                 updated = await self.mark_notification_read(data.get('notification_id'))
#                 if updated:
#                     await self.send(text_data=json.dumps(updated))
#             elif action == 'ping':
#                 await self.send(text_data=json.dumps({'type': 'pong'}))
#         except json.JSONDecodeError:
#             await self.send(text_data=json.dumps({'error': 'Invalid JSON'}))

#     async def send_notification(self, event):
#         await self.send(text_data=json.dumps({
#             'type': 'notification',
#             'notification_id': event['notification_id'],
#             'message': event['message'],
#             'ticket_id': event.get('ticket_id'),
#             'created_at': event['created_at'],
#             'is_read': event['is_read'],
#             'is_automatic': event.get('is_automatic', False)
#         }))

#     @database_sync_to_async
#     def mark_notification_read(self, notification_id):
#         try:
#             notification = Notification.objects.get(id=notification_id, user=self.user)
#             notification.is_read = True
#             notification.save()
#             return {
#                 'type': 'notification',
#                 'notification_id': notification.id,
#                 'message': notification.message,
#                 'ticket_id': notification.ticket_id,
#                 'created_at': notification.created_at.isoformat(),
#                 'is_read': True,
#                 'is_automatic': notification.is_automatic
#             }
#         except Notification.DoesNotExist:
#             return None

#     @database_sync_to_async
#     def get_unread_notifications(self):
#         return list(Notification.objects.filter(user=self.user, is_read=False).values(
#             'id', 'message', 'ticket_id', 'created_at', 'is_read', 'is_automatic'
#         ))

#     async def send_unread_notifications(self):
#         notifications = await self.get_unread_notifications()
#         for notif in notifications:
#             notif['notification_id'] = notif.pop('id')
#             notif['created_at'] = notif['created_at'].isoformat()
#             await self.send_notification(notif)
# ticketing/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from ticketing.models import Notification
from scheduling.models import Organization, Department

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close(code=4001)
            return
        
        self.user_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        self.groups = [self.user_group]
        await self.channel_layer.group_add('global', self.channel_name)
        self.groups.append('global')

        if self.user.organization:
            org_group = f"org_{self.user.organization.id}"
            await self.channel_layer.group_add(org_group, self.channel_name)
            self.groups.append(org_group)

        if hasattr(self.user, 'worker_profile') and self.user.worker_profile.department:
            dept_group = f"dept_{self.user.worker_profile.department.id}"
            await self.channel_layer.group_add(dept_group, self.channel_name)
            self.groups.append(dept_group)

        await self.accept()
        await self.send_unread_notifications()

    async def disconnect(self, close_code):
        for group in getattr(self, 'groups', []):
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            if action == 'mark_read':
                updated = await self.mark_notification_read(data.get('notification_id'))
                if updated:
                    await self.send(text_data=json.dumps(updated))
            elif action == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON'}))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_id': event['notification_id'],
            'message': event['message'],
            'ticket_id': event.get('ticket_id'),
            'created_at': event['created_at'],
            'is_read': event['is_read'],
            'is_automatic': event.get('is_automatic', False)
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.is_read = True
            notification.save()
            return {
                'type': 'notification',
                'notification_id': notification.id,
                'message': notification.message,
                'ticket_id': notification.ticket_id,
                'created_at': notification.created_at.isoformat(),
                'is_read': True,
                'is_automatic': notification.is_automatic
            }
        except Notification.DoesNotExist:
            return None

    @database_sync_to_async
    def get_unread_notifications(self):
        return list(Notification.objects.filter(user=self.user, is_read=False).values(
            'id', 'message', 'ticket_id', 'created_at', 'is_read', 'is_automatic'
        ))

    async def send_unread_notifications(self):
        notifications = await self.get_unread_notifications()
        for notif in notifications:
            notif['notification_id'] = notif.pop('id')
            notif['created_at'] = notif['created_at'].isoformat()
            await self.send_notification(notif)