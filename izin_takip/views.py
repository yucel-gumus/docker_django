from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'employee':
            return redirect('employee_dashboard')
        elif request.user.profile.role == 'manager':
            return redirect('manager_dashboard')
    return render(request, 'index.html')


