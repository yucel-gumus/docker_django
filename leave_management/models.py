from django.db import models
from django.contrib.auth.models import User
from datetime import time
from datetime import timedelta
from datetime import datetime, date, time


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


from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date, time


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    entry_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)
    working_hours = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    late_minutes = models.IntegerField(default=0)

    def calculate_working_hours(self):
        if self.entry_time and self.exit_time:
            entry_datetime = datetime.combine(date.today(), self.entry_time)
            exit_datetime = datetime.combine(date.today(), self.exit_time)
            delta = exit_datetime - entry_datetime
            self.working_hours = delta.total_seconds() / 3600
        else:
            self.working_hours = 0

    def calculate_late_minutes(self):
        company_start_time = time(8, 0)
        if self.entry_time and self.entry_time > company_start_time:
            entry_minutes = self.entry_time.hour * 60 + self.entry_time.minute
            start_minutes = company_start_time.hour * 60 + company_start_time.minute
            self.late_minutes = entry_minutes - start_minutes
        else:
            self.late_minutes = 0

    def deduct_leave_for_lateness(self):
        if self.late_minutes > 0:
            profile = self.user.profile
            deduction = self.late_minutes / (8 * 60)
            if profile.annual_leave_days >= deduction:
                profile.annual_leave_days -= deduction
            else:
                profile.annual_leave_days = 0
            profile.save()

    def save(self, *args, **kwargs):
        self.calculate_working_hours()
        self.calculate_late_minutes()
        self.deduct_leave_for_lateness()
        super().save(*args, **kwargs)
