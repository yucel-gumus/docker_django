from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import employee_required, manager_required
from .forms import LeaveRequestForm
from .models import LeaveRequest
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.db import transaction
from django.shortcuts import get_object_or_404
from accounts.models import Notification
from datetime import datetime
from .models import Attendance
from datetime import  timedelta
from django.db.models import Sum
from leave_management.tasks import deduct_leave_for_lateness
from accounts.tasks import notify_manager_for_lateness
from accounts.tasks import create_notification_for_manager
from django.contrib import messages


@login_required
@employee_required
def leave_request_create(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            return redirect("leave_request_list")
    else:
        form = LeaveRequestForm()
    return render(request, "leave_management/leave_request_form.html", {"form": form})


@login_required
@employee_required
def leave_request_list(request):
    leave_requests = LeaveRequest.objects.filter(user=request.user)
    return render(
        request,
        "leave_management/leave_request_list.html",
        {"leave_requests": leave_requests},
    )


@login_required
@manager_required
@require_POST
def leave_request_approve(request, pk):
    try:
        with transaction.atomic():  
            leave_request = get_object_or_404(LeaveRequest, pk=pk)
            if leave_request.status != "pending":
                return JsonResponse(
                    {"status": "fail", "message": "İzin talebi zaten işleme alınmış."},
                    status=400,
                )

            start_date = leave_request.start_date
            end_date = leave_request.end_date
            delta = end_date - start_date
            leave_days = delta.days + 1 

            if leave_days <= 0:
                return JsonResponse(
                    {"status": "fail", "message": "Geçersiz izin tarihleri."},
                    status=400,
                )

            user_profile = leave_request.user.profile

            if user_profile.annual_leave_days < leave_days:
                return JsonResponse(
                    {
                        "status": "fail",
                        "message": "Kullanıcının yeterli izin günü yok.",
                    },
                    status=400,
                )

            user_profile.annual_leave_days -= leave_days
            user_profile.save()

            if user_profile.annual_leave_days < 3:
                managers = User.objects.filter(profile__role="manager")
                for manager in managers:
                    Notification.objects.create(
                        user=manager,
                        message=f"{leave_request.user.username} adlı personelin yıllık izni {user_profile.annual_leave_days} güne düştü.",
                    )

            leave_request.status = "approved"
            leave_request.save()

            return JsonResponse({"status": "success"})
    except LeaveRequest.DoesNotExist:
        return JsonResponse(
            {"status": "fail", "message": "İzin talebi bulunamadı."}, status=404
        )
    except Exception as e:
        return JsonResponse({"status": "fail", "message": str(e)}, status=500)


@login_required
@manager_required
@require_POST
def leave_request_reject(request, pk):
    try:
        with transaction.atomic(): 
            leave_request = get_object_or_404(LeaveRequest, pk=pk)
            if leave_request.status != "pending":
                return JsonResponse(
                    {"status": "fail", "message": "İzin talebi zaten işleme alınmış."},
                    status=400,
                )

            leave_request.status = "rejected"
            leave_request.save()

            return JsonResponse({"status": "success"})
    except LeaveRequest.DoesNotExist:
        return JsonResponse(
            {"status": "fail", "message": "İzin talebi bulunamadı."}, status=404
        )
    except Exception as e:
        return JsonResponse({"status": "fail", "message": str(e)}, status=500)


@login_required
@manager_required
def manager_leave_request_list(request):
    leave_requests = LeaveRequest.objects.all()
    return render(
        request,
        "leave_management/manager_leave_request_list.html",
        {"leave_requests": leave_requests},
    )


@login_required
@manager_required
def leave_create_for_employee(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        
        if not start_date_str or not end_date_str:
            messages.error(request, "Başlangıç ve Bitiş tarihleri boş olamaz.")
            return redirect('leave_create_for_employee') 

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        total_days = (end_date - start_date).days + 1

        user = User.objects.get(username=username)

        profile = user.profile
        new_annual_leave_days = profile.annual_leave_days - total_days

        if new_annual_leave_days < 0:
            new_annual_leave_days = 0

        leave_request = LeaveRequest.objects.create(
            user=user,
            start_date=start_date,
            end_date=end_date,
            reason=request.POST.get('reason'),
            status="approved"
        )

        profile.annual_leave_days = new_annual_leave_days
        profile.save()

        if profile.annual_leave_days < 3:
                managers = User.objects.filter(profile__role="manager")
                for manager in managers:
                    Notification.objects.create(
                        user=manager,
                        message=f"{leave_request.user.username} adlı personelin yıllık izni {profile.annual_leave_days} güne düştü.",
                    )

        messages.success(request, f"{user.username} için {total_days} gün izin tanımlandı.")
        
        return redirect('manager_leave_request_list')  

    return render(request, 'leave_management/leave_create_for_employee.html', {'users': User.objects.all()})


@login_required
@employee_required
def record_entry(request):
    if request.method == 'POST':
        today = datetime.now().date()
        now = datetime.now().time()

        attendance, created = Attendance.objects.get_or_create(user=request.user, date=today)
        if created:
            attendance.entry_time = now
            attendance.calculate_late_minutes()
            attendance.save()

            if attendance.late_minutes > 0:
                notify_manager_for_lateness.delay(
                    user_id=request.user.id,
                    late_minutes=attendance.late_minutes
                )
                deduct_leave_for_lateness.delay(
                    user_id=request.user.id,
                    late_minutes=attendance.late_minutes
                )

            return JsonResponse({'status': 'success', 'message': 'Giriş kaydedildi.'})
        else:
            return JsonResponse({'status': 'fail', 'message': 'Bugün için zaten giriş kaydı var.'})


@login_required
@employee_required
def record_exit(request):
    if request.method == 'POST':
        today = datetime.now().date()
        now = datetime.now().time()

        attendance = Attendance.objects.filter(user=request.user, date=today).first()
        if attendance:
            attendance.exit_time = now
            attendance.calculate_working_hours()
            attendance.save()
            return JsonResponse({'status': 'success', 'message': 'Çıkış kaydedildi.'})
        else:
            return JsonResponse({'status': 'fail', 'message': 'Bugün için giriş kaydı bulunamadı.'})




@login_required
@manager_required
def monthly_work_summary(request):
    current_month = datetime.now().month
    current_year = datetime.now().year

    attendance_data = Attendance.objects.filter(
        date__year=current_year,
        date__month=current_month
    ).values('user__username').annotate(total_working_hours=Sum('working_hours'))

    return render(request, 'leave_management/monthly_summary.html', {
        'attendance_data': attendance_data,
        'month': current_month,
        'year': current_year,
    })
