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
        with transaction.atomic():  # Veritabanı işlemlerini atomik hale getirir
            leave_request = get_object_or_404(LeaveRequest, pk=pk)
            if leave_request.status != "pending":
                return JsonResponse(
                    {"status": "fail", "message": "İzin talebi zaten işleme alınmış."},
                    status=400,
                )

            # İzin süresini hesapla
            start_date = leave_request.start_date
            end_date = leave_request.end_date
            delta = end_date - start_date
            leave_days = delta.days + 1  # Başlangıç ve bitiş günlerini dahil et

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

            # İzin günlerini düş
            user_profile.annual_leave_days -= leave_days
            user_profile.save()

            if user_profile.annual_leave_days < 3:
                managers = User.objects.filter(profile__role="manager")
                for manager in managers:
                    Notification.objects.create(
                        user=manager,
                        message=f"{leave_request.user.username} adlı personelin yıllık izni {user_profile.annual_leave_days} güne düştü.",
                    )

            # İzin talebini onayla
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
        with transaction.atomic():  # Veritabanı işlemlerini atomik hale getirir
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
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            username = request.POST.get("username")
            try:
                user = User.objects.get(username=username)
                leave_request.user = user
                leave_request.status = "approved"
                leave_request.save()
                return redirect("manager_leave_request_list")
            except User.DoesNotExist:
                messages.error(request, "Kullanıcı bulunamadı.")
    else:
        form = LeaveRequestForm()
    users = User.objects.filter(profile__role="employee")
    return render(
        request,
        "leave_management/leave_create_for_employee.html",
        {"form": form, "users": users},
    )


@login_required
@employee_required
def record_entry(request):
    if request.method == 'POST':
        today = datetime.now().date()
        now = datetime.now().time()

        # Günlük giriş kaydı
        attendance, created = Attendance.objects.get_or_create(user=request.user, date=today)
        if created:
            attendance.entry_time = now
            attendance.calculate_late_minutes()
            attendance.save()

            # Geç kalma bildirimi oluştur
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

        # Günlük çıkış kaydı
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
    # Geçerli ay ve yılı alın
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Kullanıcı bazında çalışma saatlerini topla
    attendance_data = Attendance.objects.filter(
        date__year=current_year,
        date__month=current_month
    ).values('user__username').annotate(total_working_hours=Sum('working_hours'))

    return render(request, 'leave_management/monthly_summary.html', {
        'attendance_data': attendance_data,
        'month': current_month,
        'year': current_year,
    })
