from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_notification_to_user(user_id, message):
    channel_layer = get_channel_layer()
    group_name = f"user_{user_id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "message": message
        }
    )
