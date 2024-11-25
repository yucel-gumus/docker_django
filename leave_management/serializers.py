
from rest_framework import serializers
from .models import LeaveRequest
from django.contrib.auth.models import User

class LeaveRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'start_date', 'end_date', 'reason', 'status', 'requested_at', 'username']
