import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
#from .models import Shift


class ShiftConsumer(AsyncWebsocketConsumer):
    from .models import Shift
    from .serializers import ShiftSerializer
    async def connect(self):
        # Add this connection to the "shifts" group for real‑time broadcast.
        await self.channel_layer.group_add("shifts", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove this connection from the "shifts" group.
        await self.channel_layer.group_discard("shifts", self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get("action") == "update_shift":
                shift_data = data.get("shift")
                if shift_data and "id" in shift_data:
                    # Retrieve and update shift asynchronously.
                    shift = await sync_to_async(Shift.objects.get)(pk=shift_data["id"])
                    for field, value in shift_data.items():
                        if field != "id":
                            setattr(shift, field, value)
                    await sync_to_async(shift.save)()  # Auto-save the updated shift.
                    response = ShiftSerializer(shift).data
                    # Broadcast updated shift data to all clients in the "shifts" group.
                    await self.channel_layer.group_send(
                        "shifts",
                        {
                            "type": "shift_update",
                            "data": response,
                        }
                    )
                else:
                    await self.send(json.dumps({"error": "Shift data missing or invalid."}))
            else:
                await self.send(json.dumps({"error": "Invalid action specified."}))
        except Exception as e:
            # Send any error encountered back to the client.
            await self.send(json.dumps({"error": f"An error occurred: {str(e)}"}))

    async def shift_update(self, event):
        # When receiving a broadcast update, send it to the connected client.
        await self.send(json.dumps(event["data"]))
