from django.urls import path, include
from . import views
from .api_views import (
    LeaveRequestViewSet,
    LeaveRequestDataView,
    employee_leave_requests
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'api/leave-requests', LeaveRequestViewSet)

urlpatterns = [
    path('request/', views.leave_request_create, name='leave_request_create'),
    path('my-requests/', views.leave_request_list, name='leave_request_list'),
    path('manage/', views.manager_leave_request_list, name='manager_leave_request_list'),
    path('approve/<int:pk>/', views.leave_request_approve, name='leave_request_approve'),
    path('reject/<int:pk>/', views.leave_request_reject, name='leave_request_reject'),
    path('create-for-employee/', views.leave_create_for_employee, name='leave_create_for_employee'),
    path('api/my-leave-requests/', employee_leave_requests, name='employee_leave_requests'),
    path('api/leave-request-data/', LeaveRequestDataView.as_view(), name='leave_request_data'),
    path('', include(router.urls)),
]
