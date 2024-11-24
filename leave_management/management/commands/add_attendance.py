from django.core.management.base import BaseCommand
from leave_management.models import Attendance
from django.contrib.auth.models import User
from datetime import datetime, time
from accounts.tasks import notify_manager_for_lateness

class Command(BaseCommand):
    help = 'Test amaçlı Attendance tablosuna veri ekler.'

    def handle(self, *args, **kwargs):
        user = User.objects.get(id=2)  # Örnek bir kullanıcı
        if not user:
            self.stdout.write(self.style.ERROR('Kullanıcı bulunamadı!'))
            return

        # Giriş ve çıkış saatleri
        entry_time = time(10, 0)  # Geç giriş
        exit_time = time(17, 0)

        # Attendance kaydı oluştur
        attendance = Attendance.objects.create(
            user=user,
            date=datetime.now().date(),
            entry_time=entry_time,
            exit_time=exit_time
        )
        attendance.calculate_late_minutes()  # Geç kalma süresini hesapla
        attendance.save()

        # Geç kalma varsa bildirim gönder
        if attendance.late_minutes > 0:
            notify_manager_for_lateness.delay(
                user_id=user.id,
                late_minutes=attendance.late_minutes
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Attendance kaydı eklendi: {attendance}, Geç Kalma: {attendance.late_minutes} dakika'
            )
        )
