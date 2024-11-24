from django.urls import path
from . import views
from .api_views import EmployeeDataView

urlpatterns = [
    path('employee/login/', views.employee_login, name='employee_login'),
    path('employee/logout/', views.employee_logout, name='employee_logout'),
    path('manager/login/', views.manager_login, name='manager_login'),
    path('manager/logout/', views.manager_logout, name='manager_logout'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('api/employee_data/', EmployeeDataView.as_view(), name='employee_data'),
    path('manager/employee-list/', views.employee_list, name='employee_list'),
    path('notifications/read/<int:pk>/', views.mark_notification_as_read, name='mark_notification_as_read'),

]
