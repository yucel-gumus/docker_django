from celery import shared_task
from accounts.models import Profile

@shared_task
def deduct_leave_for_lateness(user_id, late_minutes):
    try:
        profile = Profile.objects.get(user_id=user_id)
        leave_to_deduct = late_minutes / 60  
        profile.remaining_leave_days -= leave_to_deduct
        if profile.remaining_leave_days < 0:
            profile.remaining_leave_days = 0  
        profile.save()
    except Profile.DoesNotExist:
        print(f"Profile bulunamadı: {user_id}")
