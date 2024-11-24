# your_project_name/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "admin"  # Ensure this matches

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # WebSocket bağlantısı kapandığında admin grubundan çık
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Log to verify message received
        print(f"Received message: {message}")

        # Admin grubuna mesaj gönder
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "attendance_notification", "message": message},
        )

    async def attendance_notification(self, event):
        # Admin grubuna gönderilen mesajı WebSocket ile gönder
        message = event["message"]
        print(f"Consumer received message: {message}")  # Add this line
        await self.send(text_data=json.dumps({"message": message}))
