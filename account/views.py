"""
Views for accounting api
"""
from datetime import datetime , timedelta

from django.utils.timezone import make_aware

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Accounting
from account import serializers

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AccountingViewSet(viewsets.ModelViewSet):
    """View for managing accounting APIs"""
    serializer_class = serializers.AccountingDetailSerializer
    queryset = Accounting.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the accounting for the authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-date')

    def get_serializer_class(self):
        """Return the serializer class for the request"""
        if self.action == 'list':
            return serializers.AccountingSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new accounting"""
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get accounting records within a date range \
            (default: current month) ex: /api/accounting/?from=2021-01-01&end=2021-01-31",
        manual_parameters=[
            openapi.Parameter(
                name='from',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Start date',
                required=False,
            ),
            openapi.Parameter(
                name='end',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='End date',
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """Handle GET requests for accounting records within a date range"""
        from_date = request.query_params.get('from')
        end_date = request.query_params.get('end')

        queryset = self.get_queryset()

        if from_date and end_date:
            from_date = make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            queryset = queryset.filter(date__range=[from_date, end_date]).order_by('-date')
        else:
            now = datetime.now()
            first_day = now.replace(day=1)

            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)

            last_day = next_month - timedelta(days=1)
            from_date = first_day
            end_date = last_day

            queryset = self.get_queryset().filter(date__range=[first_day, last_day])

        serializer = self.get_serializer(queryset, many=True)
        response_data={
            'from': from_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'data': serializer.data
        }
        return Response(response_data)
