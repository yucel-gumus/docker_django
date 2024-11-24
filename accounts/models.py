from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = (
        ('employee', 'Personel'),
        ('manager', 'Yetkili'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    hire_date = models.DateField(auto_now_add=True)
    annual_leave_days = models.PositiveIntegerField(default=15)

    def __str__(self):
        return self.user.username

# Kullanıcı oluşturulduğunda otomatik olarak Profil oluşturma
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
