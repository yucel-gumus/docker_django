from celery import shared_task
from django.contrib.auth.models import User
from .models import Notification
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task
def create_notification_for_manager(username, remaining_days):
    # Yetkililere bildirim oluştur
    managers = User.objects.filter(profile__role="manager")
    for manager in managers:
        Notification.objects.create(
            user=manager,
            message=f"{username} adlı personelin yıllık izni {remaining_days} güne düştü.",
        )
    return "success"


@shared_task
def notify_manager_for_lateness(user_id, late_minutes):
    try:
        user = User.objects.get(id=user_id)
        managers = User.objects.filter(
            profile__role="manager"
        )  # Manager rolündeki kullanıcıları al
        for manager in managers:
            Notification.objects.create(
                user=manager,
                message=f"{user.username} bugün {late_minutes} dakika geç kaldı.",
                created_at=datetime.now(),  # Correct usage of datetime.now()
            )

        message = f"{user.username} bugün {late_minutes} dakika geç kaldı."

        # WebSocket kanalına mesaj gönder
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "admin",  # Make sure the group name matches the one in your consumer
            {
                "type": "attendance_notification",  # This should match the method name in your consumer
                "message": message,
            },
        )
    except User.DoesNotExist:
        print(f"User with id {user_id} not found.")
