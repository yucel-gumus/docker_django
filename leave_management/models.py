from django.db import models
from django.contrib.auth.models import User


class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Beklemede"),
        ("approved", "Onaylandı"),
        ("rejected", "Reddedildi"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.start_date} to {self.end_date}"

    def save(self, *args, **kwargs):
        if self.status == "approved" and not self.pk:
            total_days = (self.end_date - self.start_date).days + 1
            self.user.profile.annual_leave_days -= total_days
            self.user.profile.save()
        super(LeaveRequest, self).save(*args, **kwargs)
