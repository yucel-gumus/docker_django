import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "admin" 

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        print(f"Received message: {message}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "attendance_notification", "message": message},
        )

    async def attendance_notification(self, event):
        message = event["message"]
        print(f"Consumer received message: {message}")  # Add this line
        await self.send(text_data=json.dumps({"message": message}))
