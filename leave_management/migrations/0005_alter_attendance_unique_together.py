# Generated by Django 4.2.16 on 2024-11-25 10:07

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("leave_management", "0004_remove_attendance_total_working_hours_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="attendance",
            unique_together={("user", "date")},
        ),
    ]
