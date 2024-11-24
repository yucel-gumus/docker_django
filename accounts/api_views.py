from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import EmployeeSerializer
from django.core.paginator import Paginator
from django.db.models import Q

class EmployeeDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # DataTables parametrelerini al
        draw = request.GET.get('draw')
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')

        # Filtreleme
        employees = User.objects.filter(profile__role='employee')
        if search_value:
            employees = employees.filter(
                Q(username__icontains=search_value) |
                Q(email__icontains=search_value) |
                Q(profile__role__icontains=search_value)
            )

        total = employees.count()

        # Sayfalama
        paginator = Paginator(employees, length)
        page_number = start // length + 1
        page_obj = paginator.get_page(page_number)

        # Serializer
        serializer = EmployeeSerializer(page_obj.object_list, many=True)

        # DataTables formatına uygun cevap
        response = {
            'draw': draw,
            'recordsTotal': total,
            'recordsFiltered': total,
            'data': serializer.data,
        }
        return Response(response)
