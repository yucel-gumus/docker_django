from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class EmployeeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role')
    hire_date = serializers.DateField(source='profile.hire_date')
    annual_leave_days = serializers.IntegerField(source='profile.annual_leave_days')

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'hire_date', 'annual_leave_days']
