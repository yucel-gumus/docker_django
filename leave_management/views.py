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

@login_required
@employee_required
def leave_request_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            return redirect('leave_request_list')
    else:
        form = LeaveRequestForm()
    return render(request, 'leave_management/leave_request_form.html', {'form': form})

@login_required
@employee_required
def leave_request_list(request):
    leave_requests = LeaveRequest.objects.filter(user=request.user)
    return render(request, 'leave_management/leave_request_list.html', {'leave_requests': leave_requests})

@login_required
@manager_required
@require_POST
def leave_request_approve(request, pk):
    try:
        with transaction.atomic():  # Veritabanı işlemlerini atomik hale getirir
            leave_request = get_object_or_404(LeaveRequest, pk=pk)
            if leave_request.status != 'pending':
                return JsonResponse({'status': 'fail', 'message': 'İzin talebi zaten işleme alınmış.'}, status=400)
            
            # İzin süresini hesapla
            start_date = leave_request.start_date
            end_date = leave_request.end_date
            delta = end_date - start_date
            leave_days = delta.days + 1  # Başlangıç ve bitiş günlerini dahil et

            if leave_days <= 0:
                return JsonResponse({'status': 'fail', 'message': 'Geçersiz izin tarihleri.'}, status=400)

            user_profile = leave_request.user.profile

            if user_profile.annual_leave_days < leave_days:
                return JsonResponse({'status': 'fail', 'message': 'Kullanıcının yeterli izin günü yok.'}, status=400)
            
            # İzin günlerini düş
            user_profile.annual_leave_days -= leave_days
            user_profile.save()

            # İzin talebini onayla
            leave_request.status = 'approved'
            leave_request.save()

            return JsonResponse({'status': 'success'})
    except LeaveRequest.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'İzin talebi bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'fail', 'message': str(e)}, status=500)


@login_required
@manager_required
@require_POST
def leave_request_reject(request, pk):
    try:
        with transaction.atomic():  # Veritabanı işlemlerini atomik hale getirir
            leave_request = get_object_or_404(LeaveRequest, pk=pk)
            if leave_request.status != 'pending':
                return JsonResponse({'status': 'fail', 'message': 'İzin talebi zaten işleme alınmış.'}, status=400)
            
            leave_request.status = 'rejected'
            leave_request.save()

            return JsonResponse({'status': 'success'})
    except LeaveRequest.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'İzin talebi bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'fail', 'message': str(e)}, status=500)
@login_required
@manager_required
def manager_leave_request_list(request):
    leave_requests = LeaveRequest.objects.all()
    return render(request, 'leave_management/manager_leave_request_list.html', {'leave_requests': leave_requests})


@login_required
@manager_required
def leave_create_for_employee(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            username = request.POST.get('username')
            try:
                user = User.objects.get(username=username)
                leave_request.user = user
                leave_request.status = 'approved'
                leave_request.save()
                return redirect('manager_leave_request_list')
            except User.DoesNotExist:
                messages.error(request, 'Kullanıcı bulunamadı.')
    else:
        form = LeaveRequestForm()
    users = User.objects.filter(profile__role='employee')
    return render(request, 'leave_management/leave_create_for_employee.html', {'form': form, 'users': users})

