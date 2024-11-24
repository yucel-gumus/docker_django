from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings  # Ayarları içe aktarın

# Django'nun ayarlarını Celery'e yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'izin_takip.settings')  # Proje adınızı kullanın

app = Celery('izin_takip')  # Proje adınızı kullanın

# Django ayarlarından Celery için varsayılan yapılandırmayı al
app.config_from_object('django.conf:settings', namespace='CELERY')

# Görevleri uygulamalardan otomatik keşfet
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
