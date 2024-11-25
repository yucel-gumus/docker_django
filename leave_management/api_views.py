from rest_framework import viewsets
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    İzin taleplerini listeleme, oluşturma, güncelleme ve silme işlemleri.
    """

    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]


@swagger_auto_schema(
    method="get", operation_description="Personelin izin taleplerini getirir."
)
@api_view(["GET"])
def employee_leave_requests(request):
    leave_requests = LeaveRequest.objects.filter(user=request.user)
    serializer = LeaveRequestSerializer(leave_requests, many=True)
    return Response({"data": serializer.data})


class LeaveRequestDataView(APIView):
    """
    DataTables için izin taleplerinin sunucu taraflı verilmesi.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        draw = request.GET.get("draw")
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))
        search_value = request.GET.get("search[value]", "")

        leave_requests = LeaveRequest.objects.all()
        if search_value:
            leave_requests = leave_requests.filter(
                Q(user__username__icontains=search_value)
                | Q(status__icontains=search_value)
                | Q(reason__icontains=search_value)
            )

        total = leave_requests.count()

        paginator = Paginator(leave_requests, length)
        page_number = start // length + 1
        page_obj = paginator.get_page(page_number)

        serializer = LeaveRequestSerializer(page_obj.object_list, many=True)

        response = {
            "draw": draw,
            "recordsTotal": LeaveRequest.objects.count(),
            "recordsFiltered": leave_requests.count(),
            "data": serializer.data,
        }
        return Response(response)
