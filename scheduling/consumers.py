# # scheduling/consumers.py
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# from .models import Shift
# from .serializers import ShiftSerializer
# from rolepermissions.checkers import has_permission
# from ticketing.utils import send_automatic_notification

# class ShiftConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope['user']
#         if self.user.is_anonymous:
#             await self.close()
#         await self.channel_layer.group_add("shifts", self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("shifts", self.channel_name)

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         if data.get("action") == "update_shift":
#             if not (has_permission(self.user, 'manage_department') or has_permission(self.user, 'manage_organization')):
#                 await self.send(json.dumps({"error": "Permission denied."}))
#                 return
#             shift_data = data.get("shift")
#             shift = await sync_to_async(Shift.objects.get)(pk=shift_data["id"])
#             old_workers = set(await sync_to_async(lambda: list(shift.workers.all()))())
            
#             for field, value in shift_data.items():
#                 if field != "id":
#                     if field == "workers":
#                         await sync_to_async(shift.workers.clear)()
#                         await sync_to_async(shift.workers.add)(*value)
#                     else:
#                         setattr(shift, field, value)
#             await sync_to_async(shift.save)()
            
#             new_workers = set(await sync_to_async(lambda: list(shift.workers.all()))())
#             added = new_workers - old_workers
#             removed = old_workers - new_workers
            
#             if added:
#                 send_automatic_notification(
#                     users=[worker.user for worker in added],
#                     message=f"You have been added to a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
#                 )
#             if removed:
#                 send_automatic_notification(
#                     users=[worker.user for worker in removed],
#                     message=f"You have been removed from a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
#                 )
            
#             response = ShiftSerializer(shift).data
#             await self.channel_layer.group_send("shifts", {"type": "shift_update", "data": response})

#     async def shift_update(self, event):
#         await self.send(json.dumps(event["data"]))
# scheduling/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Shift
from .serializers import ShiftSerializer
from core.permissions import has_permission
from ticketing.utils import send_automatic_notification

class ShiftConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
        await self.channel_layer.group_add("shifts", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("shifts", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "update_shift":
            if not (has_permission(self.user, 'edit_shift') or has_permission(self.user, 'manage_organization')):
                await self.send(json.dumps({"error": "Permission denied."}))
                return
            shift_data = data.get("shift")
            shift = await sync_to_async(Shift.objects.get)(pk=shift_data["id"])
            old_workers = set(await sync_to_async(lambda: list(shift.workers.all()))())
            
            for field, value in shift_data.items():
                if field != "id":
                    if field == "workers":
                        await sync_to_async(shift.workers.clear)()
                        workers = await sync_to_async(Worker.objects.filter)(id__in=value)
                        await sync_to_async(shift.workers.add)(*workers)
                    else:
                        setattr(shift, field, value)
            await sync_to_async(shift.save)()
            
            new_workers = set(await sync_to_async(lambda: list(shift.workers.all()))())
            added = new_workers - old_workers
            removed = old_workers - new_workers
            
            if added:
                send_automatic_notification(
                    users=[worker.user for worker in added],
                    message=f"You have been added to a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
                )
            if removed:
                send_automatic_notification(
                    users=[worker.user for worker in removed],
                    message=f"You have been removed from a {shift.shift_type} shift on {shift.start_time.strftime('%Y-%m-%d %H:%M')}."
                )
            
            response = ShiftSerializer(shift).data
            await self.channel_layer.group_send("shifts", {"type": "shift_update", "data": response})

    async def shift_update(self, event):
        await self.send(json.dumps(event["data"]))