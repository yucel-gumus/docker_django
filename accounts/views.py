from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import employee_required, manager_required
from django.contrib import messages
from django.contrib.auth.models import User

def employee_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.profile.role == 'employee':
            login(request, user)
            return redirect('employee_dashboard')
        else:
            messages.error(request, 'Geçersiz kimlik bilgileri.')
    return render(request, 'accounts/employee_login.html')

def manager_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.profile.role == 'manager':
            login(request, user)
            return redirect('manager_dashboard')
        else:
            messages.error(request, 'Geçersiz kimlik bilgileri.')
    return render(request, 'accounts/manager_login.html')

@login_required
@employee_required
def employee_dashboard(request):
    remaining_leave_days = request.user.profile.annual_leave_days
    return render(request, 'accounts/employee_dashboard.html',{'remaining_leave_days': remaining_leave_days})

@login_required
@manager_required
def manager_dashboard(request):
    return render(request, 'accounts/manager_dashboard.html')

def employee_logout(request):
    logout(request)
    return redirect('employee_login')

def manager_logout(request):
    logout(request)
    return redirect('manager_login')


@login_required
@manager_required
def employee_list(request):
    employees = User.objects.filter(profile__role='employee')
    return render(request, 'accounts/employee_list.html', {'employees': employees})