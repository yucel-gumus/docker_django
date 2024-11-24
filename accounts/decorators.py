from django.shortcuts import redirect

def employee_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.profile.role == 'employee':
            return view_func(request, *args, **kwargs)
        else:
            return redirect('manager_dashboard')
    return wrapper_func

def manager_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.profile.role == 'manager':
            return view_func(request, *args, **kwargs)
        else:
            return redirect('employee_dashboard')
    return wrapper_func
