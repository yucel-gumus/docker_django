from celery import shared_task
from django.contrib.auth.models import User
from .models import Notification

@shared_task
def create_notification_for_manager(username, remaining_days):
    # Yetkililere bildirim oluştur
    managers = User.objects.filter(profile__role='manager')
    for manager in managers:
        Notification.objects.create(
            user=manager,
            message=f"{username} adlı personelin yıllık izni {remaining_days} güne düştü."
        )
